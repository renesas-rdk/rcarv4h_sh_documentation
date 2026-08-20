Deploying to the Target Board
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Target Deployment Locations
"""""""""""""""""""""""""""

Only two artifacts are deployed to the target board:

.. list-table::
   :header-rows: 1
   :widths: 25 30 45

   * - Artifact
     - Target location
     - Purpose
   * - FIT image
     - ``/boot/fitImage``
     - Boot image loaded by U-Boot. Contains the kernel, the base DTB, the device tree overlays,
       the BL31 blob and the initramfs.
   * - Kernel modules
     - |modules_path|
     - Loadable kernel drivers and other kernel components used at runtime.

.. note::

   The ``.dtb`` and ``.dtbo`` files are not copied to the board separately. U-Boot reads the device
   tree and the selected overlay from inside ``fitImage``.

Copying Files from the Build Host to the Target Board
"""""""""""""""""""""""""""""""""""""""""""""""""""""

.. tip::

   If you change only the device tree sources and leave the kernel configuration and source code
   untouched, no kernel module changes are produced. In that case ``./main_build.sh fitimage all``
   is the only build command needed, and only the rebuilt ``fitImage`` has to be copied.

.. important::

   Before overwriting any existing files on the target board, back up the current FIT image and
   kernel modules so that you can restore them if needed.

Run the following commands on the **target board** to copy the generated artifacts from the build host over SSH by using ``rsync``.

Install ``rsync`` on the target board if it is not already installed:

.. code-block:: bash

   sudo apt update
   sudo apt install rsync

Set environment variables:

.. code-block:: bash

   export BUILD_USER=<build-host-user>
   export BUILD_HOST=<build-host-ip>
   # Absolute paths on the build host. Do not use "~": it would expand on the target board.
   export FIT_OUTPUT_DIR=/home/<build-host-user>/rcarv4h_workspace/rcar-utils/workspace/fitimage
   export KERNEL_MODULES_OUTPUT_DIR=/home/<build-host-user>/rcarv4h_workspace/rcar-utils/workspace/kernel-modules

.. note::

   ``FIT_OUTPUT_DIR`` and ``KERNEL_MODULES_OUTPUT_DIR`` refer to directories on the **build host**.
   The values above are the default layout, under the ``rcar-utils`` checkout; change them if you
   uncommented those settings in ``config.ini``. They must be absolute paths: a leading ``~`` is
   expanded by the local shell on the target board before ``rsync`` runs, which resolves to the
   wrong directory.

   The ``rsync`` commands below run under ``sudo``, so the SSH connection uses the ``root``
   credentials of the target board. Make sure ``root`` on the target can log in to the build host,
   or copy the files to a temporary directory as a normal user first and then move them into place
   with ``sudo``.

Copy the FIT image:

.. code-block:: bash

   sudo rsync -avz "${BUILD_USER}@${BUILD_HOST}:${FIT_OUTPUT_DIR}/fitImage" /boot/fitImage

Copy the kernel modules. Which command to use depends on whether you also rebuilt the out-of-tree
kernel modules.

**If you rebuilt the out-of-tree modules** with ``./main_build.sh ext-modules install`` on top of
``./main_build.sh kernel modules-install``, the output directory holds the complete module set and
is synchronized as a whole:

.. code-block:: bash

   sudo rsync -avz --delete-during \
     "${BUILD_USER}@${BUILD_HOST}:${KERNEL_MODULES_OUTPUT_DIR}/usr/lib/modules/6.18.39-arm64-renesas/" \
     /usr/lib/modules/6.18.39-arm64-renesas/

**If you built only the in-tree modules** with ``./main_build.sh kernel modules-install``, the
out-of-tree modules already installed on the board must be preserved:

.. code-block:: bash

   sudo rsync -avz --delete-during \
     --exclude='extra/' \
     --exclude='updates/' \
     "${BUILD_USER}@${BUILD_HOST}:${KERNEL_MODULES_OUTPUT_DIR}/usr/lib/modules/6.18.39-arm64-renesas/" \
     /usr/lib/modules/6.18.39-arm64-renesas/

.. caution::

   The ``extra/`` and ``updates/`` directories hold the out-of-tree kernel modules described in
   :ref:`Building the Out-of-Tree Kernel Modules <build_ext_modules>`. The ``kernel
   modules-install`` target does not produce them, so ``--delete-during`` would remove them from
   the board unless both directories are excluded.

   If they are accidentally removed, rebuild them with ``./main_build.sh ext-modules install``,
   restore them from a backup, or copy them from the original image of the R-Car/V4H SH.

Both targets also generate configuration files outside ``usr/lib/modules/``. They are already present
on the original image of the R-Car/V4H SH, so they only need to be copied when you deploy to a
fresh root filesystem or change them:

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - File in ``KERNEL_MODULES_OUTPUT_DIR``
     - Purpose
   * - ``usr/lib/modules-load.d/uio_pdrv_genirq.conf``,
       ``usr/lib/modprobe.d/uio_pdrv_genirq.conf``
     - Load ``uio_pdrv_genirq`` and pass it the ``of_id`` parameter. Without it no
       ``generic-uio`` node binds.
   * - ``usr/lib/modules-load.d/cmemdrv.conf``,
       ``usr/lib/modprobe.d/cmemdrv.conf``
     - Load ``cmemdrv`` at boot and reserve memory for it, installed by ``ext-modules install``.
   * - ``usr/lib/modules-load.d/pvrsrvkm.conf``
     - Load ``pvrsrvkm`` at boot, installed by ``ext-modules install``.
   * - ``usr/lib/firmware/rcar_gen4_pcie.bin``,
       ``usr/lib/firmware/LICENCE.r8a779g_pcie_phy``
     - PCIe PHY firmware, installed by ``kernel modules-install``. The
       ``pcie-rcar-gen4`` module requests it every time it probes, so without it the PCIe link
       never comes up and NVMe devices do not appear. It is not part of the ``linux-firmware``
       package.
   * - ``usr/lib/firmware/rgx.fw.*``, ``usr/lib/firmware/rgx.sh.*``
     - PowerVR GPU firmware, installed by ``ext-modules install``. Must match the ``pvrsrvkm``
       module.

After copying the files, update module dependencies on the target device:

.. code-block:: bash

   sudo depmod 6.18.39-arm64-renesas

Reboot the target board to apply the updated kernel, device tree, and modules:

.. code-block:: bash

   sudo reboot

Verifying the Update
""""""""""""""""""""

After the board has rebooted, log in and confirm that the new kernel is running:

.. code-block:: bash

   uname -r

The command should report |kernel_release|.

Check that the expected modules are loaded and that no driver failed to probe:

.. code-block:: bash

   lsmod
   dmesg --level=err,warn

If you changed the device tree, confirm that your change is visible in the live device tree:

.. code-block:: bash

   ls /proc/device-tree/

Recovering Files from an Unbootable SD Card
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the target board can no longer boot or required files have been accidentally
removed, you can restore the original files by mounting the SD card on a PC.

1. Power off the target board and remove the SD card.

2. Insert the SD card into a Linux PC or another system that can access its
   partitions.

3. Mount the root filesystem partition from the SD card:

   .. code-block:: bash
      :emphasize-lines: 3

      mkdir -p /mnt/rootfs
      # Mount the root filesystem partition (replace /dev/sdX1 with the actual device name)
      sudo mount /dev/sdX1 /mnt/rootfs

   .. note::

      The microSD card image for the R-Car/V4H SH uses a single partition that holds both ``/boot``
      and the root filesystem. Run ``lsblk`` to confirm the device name before mounting.

4. Copy the original files back to the mounted partition. The key paths to restore, relative to
   ``/mnt/rootfs``, are ``/boot`` and |modules_path|.

5. Safely unmount the partition:

   .. code-block:: bash

      sudo umount /mnt/rootfs

6. Remove the SD card from the PC, reinsert it into the target board, and power
   on the system.
