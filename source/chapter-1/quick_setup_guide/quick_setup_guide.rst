.. _quick_setup_sh_guide:

Quick start guide for R-Car/V4H SH
----------------------------------

This guide provides step-by-step instructions for setting up the R-Car/V4H Sparrow Hawk (SH) board and preparing the development environment.

Follow the sections in order. Starting from a board straight out of the box, you will end up
with Ubuntu 24.04 and ROS 2 Jazzy running on the R-Car/V4H SH:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - **Section**
     - **What you do**
   * - :ref:`Downloading the software package <sh_software_package>`
     - Download and extract the software package that contains the ``ipl-burning`` script and
       the Ubuntu 24.04 Server image.
   * - :ref:`Boot Mode Configuration (DIP Switch) <sh_boot_mode_config>`
     - Learn what each position of the Mode Switch (**SW2**) controls: boot device,
       master boot processor, and JTAG debugging function.
   * - **Common hardware setup**
     - Connect power, the serial console, and the network to the board.
   * - :ref:`Flashing the IPL <flashing_the_ipl>`
     - Write the Initial Program Loader to the board's serial flash ROM using the
       ``ipl-burning`` script.
   * - :ref:`Preparing the root file system microSD card <sh_prepare_microsd>`
     - Flash the Ubuntu 24.04 Server image onto a microSD card with ``bmaptool`` or
       Balena Etcher.
   * - **Booting the board**
     - Boot the board for the first time and watch the boot log on the serial console.
   * - :ref:`First Boot and Software Setup <first_time_boot_setup>`
     - Log in, expand the root partition to the full microSD card, and install ROS 2 Jazzy.

.. _sh_software_package:

**Downloading the software package**

Everything you need to bring up the board is distributed in a single software package: the
``ipl-burning`` script that writes the Initial Program Loader to the board, and the Ubuntu 24.04
Server image that you flash onto the microSD card. Download the package to your host PC before
you start:

`R-Car/V4H Sparrow Hawk Software package <https://github.com/renesas-rdk/rcarv4h_sh_documentation/releases>`_

Extract the ``r-car-v4h-sparrow-hawk-software-package-v***.zip`` file. The ``board_setup`` folder inside it has the following structure:

.. code-block:: text

   board_setup/
   ├── board_image/
   │   ├── ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.xz
   │   └── ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.bmap
   └── ipl-burning/
       ├── run.sh
       ├── run.bat
       └── ...

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - **Folder**
     - **Description**
   * - ``board_image/``
     - Ubuntu 24.04 Server microSD card image and its block map file.

       Used in :ref:`Preparing the root file system microSD card <sh_prepare_microsd>`.
   * - ``ipl-burning/``
     - Script that writes the Initial Program Loader to the board's serial flash ROM.

       Used in :ref:`Flashing the IPL <flashing_the_ipl>`.

The next sections of this guide assume that you have already downloaded and extracted the software package to your host PC.

.. toctree::
    :maxdepth: 2

    boot_mode_config
    hardware_setup_ipl
    prepare_microsd
    boot_and_first_setup
