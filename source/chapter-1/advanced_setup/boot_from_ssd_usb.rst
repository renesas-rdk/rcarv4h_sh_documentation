.. _boot_from_nvme:

.. _boot_from_usb:

Booting R-Car V4H SH from NVMe SSD or USB Storage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The advantages of booting from an NVMe SSD or a USB storage device include **faster read/write speeds**, improved performance, and increased storage capacity compared to booting from an SD card.

The boot flow is the same for both devices: write the root file system image to the storage device (if it does not contain one yet), then configure U-Boot to boot from that device. Only the device node and the U-Boot command differ:

.. list-table::
   :header-rows: 1
   :widths: 30 25 25 20

   * - Storage device
     - Device node
     - Root partition
     - U-Boot command
   * - M.2 NVMe SSD
     - ``/dev/nvme0n1``
     - ``/dev/nvme0n1p1``
     - ``run autoconf_nvme``
   * - USB storage device
     - ``/dev/sda``
     - ``/dev/sda1``
     - ``run autoconf_usb``

Hardware Required
"""""""""""""""""

- R-Car V4H SH board with power supply and serial console (see :ref:`Quick Setup Guide <quick_setup_sh_guide>`).
- One of the following storage devices:

  - M.2 NVMe SSD.
  - USB storage device, such as a USB flash drive or a USB SSD.

- A USB Power Delivery adapter rated at 65 W or higher.

Hardware Connection
"""""""""""""""""""

The following image shows how to connect the M.2 NVMe SSD to the onboard M.2 slot of the R-Car V4H SH:

.. figure:: ../../images/ssd_connection.png
   :alt: SSD Connection Diagram
   :align: center
   :width: 600px

   SSD Connection Diagram

A USB storage device does not require any adapter board. Plug it directly into one of the USB 3.0 Type-A ports of the R-Car V4H SH.

Detailed Steps
""""""""""""""

.. important::

   - Make sure to back up any important data on the storage device before proceeding, as the following steps will erase all existing data on it.
   - Connect the M.2 NVMe SSD to the R-Car V4H SH board before powering on the board.
   - Connect the USB storage device before you enter the U-Boot prompt, so that U-Boot can detect it.
   - Handle the M.2 NVMe SSD with care to avoid damage from static electricity.

.. note::

   The following steps assume that the NVMe SSD is detected as ``/dev/nvme0n1`` and that the USB storage device is detected as ``/dev/sda``.

   If your system detects the storage device with a different device name, replace it accordingly in the commands and examples.

Storage device preparation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   The following steps will guide you to flash the root filesystem image to the NVMe SSD or to the USB storage device. If the device already holds a root filesystem, you can skip the flashing steps and proceed to :ref:`configure the bootloader <ssd_bootloader>`.

   A USB storage device can also be flashed on a host PC exactly like a microSD card, as described in the :ref:`Quick Setup Guide <quick_setup_sh_guide>`. In that case, skip to :ref:`configure the bootloader <ssd_bootloader>` as well.

#. Prepare the storage device:

   - For an NVMe SSD: insert the M.2 NVMe SSD directly into the onboard M.2 slot of the R-Car V4H SH.
   - For a USB storage device: plug it into one of the USB 3.0 Type-A ports of the R-Car V4H SH.

#. Boot from the SD card:

   - Insert the SD card with the Ubuntu image into the R-Car V4H SH and power it on.
   - Ensure that the system boots successfully from the SD card.

#. Install the required tools:

   .. code-block:: bash

      sudo apt update
      sudo apt-get install bmap-tools

#. Flash the storage device:

   - Once booted from the SD card, open a terminal.
   - Make sure the storage device is recognized by running:

     .. code-block:: bash

        lsblk

   - Identify the storage device, for example ``/dev/nvme0n1`` for the NVMe SSD or ``/dev/sda`` for the USB storage device.
   - On your **host PC** (connected to the same network as the board), copy the ``ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.xz`` file and the ``ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.bmap`` file to the target board. ``<rcarv4h_sh_ip>`` is the board's IP address; find it by running ``ip addr`` on the board.

     .. code-block:: bash

        # Run these commands on the host PC.

        # Copy the image file to the target board
        scp ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.xz ubuntu@<rcarv4h_sh_ip>:/home/ubuntu/

        # Copy the bmap file to the target board
        scp ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.bmap ubuntu@<rcarv4h_sh_ip>:/home/ubuntu/

   - Flash the root filesystem image to the storage device by running the command matching your device:

     .. code-block:: bash

        # Please change the device name if your storage device is recognized with a different name.

        # NVMe SSD
        sudo bmaptool copy ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.xz /dev/nvme0n1

        # USB storage device
        sudo bmaptool copy ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.xz /dev/sda

#. From now on, the SD card is no longer required for booting the system. You can remove the SD card from the R-Car V4H SH.

.. _ssd_bootloader:

Configure the bootloader
~~~~~~~~~~~~~~~~~~~~~~~~

#. Make sure you can access the R-Car V4H SH board via serial console.
#. Power off the board and power it on again to access the bootloader prompt. Press any key to stop the autoboot process and access the U-Boot prompt.
#. At the U-Boot prompt, set the boot device to the NVMe SSD or to the USB storage device by running the following commands:

   If you want to boot from the storage device by default, you can set the boot command to run the corresponding boot sequence:

   .. code-block:: bash

      # NVMe SSD
      setenv bootcmd 'run autoconf_nvme'
      saveenv

      # USB storage device
      setenv bootcmd 'run autoconf_usb'
      saveenv

   Or you can manually boot from the storage device by running the corresponding command:

   .. code-block:: bash

      # NVMe SSD
      run autoconf_nvme

      # USB storage device
      run autoconf_usb

#. Verify booting from the storage device:

   - Once the system boots up, log in.
   - Verify that the root filesystem is mounted from the NVMe SSD or the USB storage device by checking the location of the root filesystem ``/``:

     .. code-block:: bash

        lsblk

#. Resize the filesystem if necessary:

   - If the storage device has a larger capacity than the original root filesystem image, you may want to resize the filesystem to use the full capacity of the device.
   - Use the following commands to resize the filesystem:

     .. code-block:: bash

        sudo apt update
        sudo apt install parted

     .. code-block:: bash

        # NVMe SSD
        sudo parted /dev/nvme0n1 resizepart 1 100%
        sudo resize2fs /dev/nvme0n1p1

     .. code-block:: bash

        # USB storage device
        sudo parted /dev/sda resizepart 1 100%
        sudo resize2fs /dev/sda1

Known Issues
""""""""""""

When booting the R-Car V4H SH from an NVMe SSD or a USB storage device, the following error message may appear on the serial console after you press the Reset button on the board:

.. code-block:: text

   "Error" handler, esr 0xbe000011
   elr: 000000000003b0d0 lr : 000000000003b0dc (reloc)
   elr: 00000000bff6d0d0 lr : 00000000bff6d0dc
   x0 : 0000000000000000 x1 : 00000000bbf31df0
   x2 : 0000000000000000 x3 : 00000000007b6c24
   x4 : 0000000000000000 x5 : 00000000bffb8618
   x6 : 0000000000000020 x7 : 0000000000000012
   x8 : 0000000000000002 x9 : 00000000bffc0b6a
   x10: 000000000000001d x11: 0000000000000022
   x12: 00000000000000fe x13: 0000000000000002
   x14: 00000000bffbdca0 x15: 00000000ffffffff
   x16: 00000000bff54e6c x17: 0000000000000000
   x18: 00000000bbf31df0 x19: 00000000bbfdfac0
   x20: 0000000000000000 x21: 00000000bbf357b0
   x22: 0000000000000003 x23: 00000000bbfdfbf0
   x24: 00000000bbfdfb68 x25: 00000000bbfdfb98
   x26: 0000000000000009 x27: 0000000000000064
   x28: 0000000000101121 x29: 00000000bbf1d930

   Code: b9080c20 f9400660 b9480c00 d5033fbf (368ffe40)
   Resetting CPU ...

   ▒esetting ...

After this message, the board resets the CPU again and boots successfully. This has no effect on system operation, and the message can be safely ignored.

This issue only occurs when the board is reset with the Reset button. It does not occur when the board is restarted with the ``reboot`` command or by pressing the Power button.

.. note::

   This issue is under investigation and will be fixed in a future release.
