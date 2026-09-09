.. _sh_prepare_microsd:

Preparing the Root File System microSD Card
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To boot the R-Car V4H SH using a microSD card, you must first flash a bootable Linux image onto it.
Two options are described below: ``bmaptool`` on Ubuntu, or Balena Etcher on Windows, macOS, or Linux.

microSD Card Requirements
"""""""""""""""""""""""""

- A host machine for flashing the image:

  - Ubuntu with ``bmaptool``, or
  - Windows, macOS, or Linux with Balena Etcher

- **microSD card**: 16 GB or larger.
  For best performance and compatibility, we recommend using the microSD card provided with the board.

- **Provided bootable files:**

  The image files come from the software package you downloaded and extracted in
  :ref:`Downloading the software package <sh_software_package>`. You can find the following
  files under the ``board_setup`` folder:

  .. list-table::
     :header-rows: 1
     :widths: 30 70

     * - **File name**
       - **Description**
     * - ``board_image/``
       - Board image files

         - ``ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.xz``: Ubuntu 24.04 Server microSD card image file containing:

           - Linux kernel image
           - Linux device tree file
           - Ubuntu 24.04 root filesystem
           - Default credentials:

             - **Username**: **ubuntu**
             - **Password**: **ubuntu**

         - ``ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.bmap``: Block map file for fast flashing with ``bmaptool``

Option 1: Flash using bmaptool (Ubuntu)
""""""""""""""""""""""""""""""""""""""""

bmaptool is a faster command-line tool for flashing images to microSD cards using block map files (bmap).
It provides quicker flashing compared to traditional methods by skipping empty blocks and verifying data integrity automatically.

#. **Install bmaptool**

   On **Ubuntu**:

   .. code-block:: bash

      sudo apt-get install bmap-tools

#. **Flashing the Image**

   a. Insert your microSD card into your machine.

   b. Identify the microSD card device name:

      .. code-block:: bash

         lsblk

      Look for your microSD card (e.g., ``/dev/sdb``). Make sure to identify it correctly.

      .. warning::

         Please confirm the microSD card device name carefully.
         Double-check to avoid overwriting your main disk.

   c. Unmount any auto-mounted partitions on the microSD card:

      .. code-block:: bash

         sudo umount /dev/sdX*

   d. Flash the image directly (no need to extract):

      .. code-block:: bash

         sudo bmaptool copy ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.xz /dev/sdX

      Replace ``/dev/sdX`` with your actual microSD card device (e.g., ``/dev/sdb``, not ``/dev/sdb1``).

      .. note::

         Please ensure that the ``.bmap`` file is in the same directory as the image file.
         bmaptool automatically detects the ``.bmap`` file with the same base name.

         You can also specify it explicitly:

         .. code-block:: bash

            sudo bmaptool copy --bmap ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.bmap \
              ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.xz /dev/sdX

   e. Wait for the process to complete. bmaptool will display progress and verify the image after flashing.

   f. Before removing the microSD card, run:

      .. code-block:: bash

         sync

Option 2: Flash using Balena Etcher
""""""""""""""""""""""""""""""""""""

Balena Etcher is a user-friendly GUI tool to flash OS images to microSD cards and USB drives.
It provides a simple and safe method.

It supports many OS platforms, including Windows, macOS, and Linux.

#. **Install Balena Etcher**

   Download and install the software from the `Balena Etcher Official Website <https://etcher.balena.io/>`_.

#. **Decompress the image file**

   If you downloaded the image as a compressed ``.xz`` file, decompress it first:

   .. code-block:: bash

      # On Linux
      xz -dk ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.xz

   Or use a decompression tool on Windows or macOS to extract the ``.img`` file.

#. **Flashing the Image**

   Once Etcher is open:

   .. figure:: ../../images/balenaetcher-eye.jpg
      :alt: Balena Etcher Application
      :width: 500px
      :align: center

      Balena Etcher Application

   a. **Select Image:** Click ``Flash from file`` and choose your image file (e.g., ``ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img``).

   b. **Select Target:** Insert your microSD card into the host machine and choose the correct device.

      .. warning::

         Please confirm the microSD card device name carefully.
         Double-check to avoid overwriting your main disk.

   c. **Flashing:** Click ``Flash`` to begin. Etcher will:

      - Write the image
      - Validate the image
      - Automatically unmount the microSD card

   d. **Finish:** Remove the microSD card safely after Etcher reports successful completion.
