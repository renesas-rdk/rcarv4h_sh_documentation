.. _quick_setup_sh_guide:

Quick start guide for R-Car V4H SH
----------------------------------

This guide provides step-by-step instructions for setting up the R-Car V4H Sparrow Hawk (SH) board and preparing the development environment.

Follow the sections in order. Starting from a board straight out of the box, you will end up
with Ubuntu 24.04 and ROS 2 Jazzy running on the R-Car V4H SH:

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
   * - :ref:`Common hardware setup <sh_common_hardware_setup>`
     - Connect power, the serial console, and the network to the board.
   * - :ref:`Flashing the IPL <flashing_the_ipl>`
     - Write the Initial Program Loader to the board's serial flash ROM using the
       ``ipl-burning`` script.
   * - :ref:`Preparing the root file system microSD card <sh_prepare_microsd>`
     - Flash the Ubuntu 24.04 Server image onto a microSD card with ``bmaptool`` or
       Balena Etcher.
   * - :ref:`Booting the board <sh_booting_the_board>`
     - Boot the board for the first time and watch the boot log on the serial console.
   * - :ref:`First Boot and Software Setup <first_time_boot_setup>`
     - Log in, expand the root partition to the full microSD card, and install ROS 2 Jazzy.

The following figure shows the same path, and where each step is carried out:

.. figure:: ../../images/quick_setup_workflow_overview.png
   :align: center
   :alt: Quick start guide workflow overview

   Quick start guide workflow overview

.. toctree::
   :maxdepth: 2

   software_package
   boot_mode_config
   hardware_setup_ipl
   prepare_microsd
   boot_and_first_setup
