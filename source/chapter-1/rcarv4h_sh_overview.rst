Overview
--------

`Sparrow Hawk (SH) <https://www.renesas.com/en/design-resources/partners/retronix/sparrow-hawk-r-car-v4h-high-performance-ai-single-board-computer-sbc>`_
is a compact and highly expandable edge AI development board. Powered by the Renesas R-Car V4H System-on-Chip (SoC) with 4 Arm® Cortex®-A76 cores and 3 Arm Cortex-R52 cores,
along with an integrated Image Signal Processor (ISP), its built-in AI engine delivers up to 30 TOPS (Tera Operations Per Second) Dense deep learning performance,
while the Imagination Technologies PowerVR AXM-8-256 (GPU) achieves over 150 GFLOPS of computing power.

Software Environment
^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - **Category**
     - **Description**
   * - **OS Support**
     - **Ubuntu 24.04**, available as headless (Server) and Desktop variants.
   * - **Default Credentials**
     - Username: **ubuntu** | Password: **ubuntu**
   * - **ROS 2 Distribution**
     - Tested with **ROS 2 Jazzy**

Hardware Environment
^^^^^^^^^^^^^^^^^^^^

**R-Car/V4H SH Board View:**

The following image shows the top view of the R-Car/V4H Sparrow Hawk (SH) board:

.. figure:: ../images/V4H_SBC.png
   :alt: R-Car/V4H SH Top View
   :width: 600px
   :align: center

   R-Car/V4H SH Top View

.. list-table:: R-Car/V4H SH Hardware Specifications
   :header-rows: 1
   :widths: 30 70

   * - Function
     - Specification
   * - CPU
     - 4x Arm® Cortex®-A76, 3x Arm® Cortex®-R52
   * - GPU
     - IMG A-Series AXM-8-256
   * - DRAM
     - 8 GB / 16 GB LPDDR5
   * - Flash Memory
     - 64 MB QSPI
   * - Camera I/F
     - 2x MIPI CSI camera
   * - Display
     - 1x DP, 1x DSI
   * - Ethernet AVB
     - 1 port (1 Gbps)
   * - Debug Serial
     - 2 ports
   * - Audio
     - In/Out, In
   * - PCIe 4.0
     - 1x M.2 Key-M (x2 lane)
   * - USB 3.0
     - 2x USB Type-A, 2x USB Type-C
   * - CAN-FD
     - 2 ports
   * - PWM
     - 1 port
   * - JTAG
     - 1 port
   * - Removable Media
     - 1x microSD
   * - Extensions
     - Raspberry Pi® 40-pin GPIO header
   * - Mode Switches
     - DIP switch
   * - Power
     - USB PD 20 V
   * - Power Control
     - 2x switch, 1x jumper

For more details about the R-Car/V4H SH specifications, visit the `R-Car Community Sparrow Hawk <https://rcar-community.github.io/Sparrow-Hawk/index.html#hardware>`_.

Development Environment
^^^^^^^^^^^^^^^^^^^^^^^

When setting up the development environment for the R-Car/V4H SH, it is important to have the necessary hardware components and software tools in place. Below is an overview of the required items and their descriptions.

R-Car/V4H SH
""""""""""""

.. list-table::
   :widths: 20 80
   :header-rows: 0

   * - R-Car/V4H SH
     - R-Car/V4H Sparrow Hawk (SH).
   * - AC Adapter
     - Must be prepared by the user: a USB Power Delivery adapter rated at 65 W or higher.
   * - DisplayPort Cable
     - Used to connect a DisplayPort monitor to the board.
       The R-Car/V4H SH provides a DisplayPort connector.
   * - USB Camera (optional)
     - Used as the camera input for demo applications.

Common
""""""

.. list-table::
   :widths: 20 80
   :header-rows: 0

   * - USB to microUSB Cable

       (provided with the R-Car/V4H SH)
     - Used to connect the board to the PC for initial setup and development.
   * - Ethernet Cable
     - Used to connect the board to the network for software installation and updates.
   * - DisplayPort Monitor
     - Used to display the graphical output of the board.
   * - microSD Card

       (provided with the R-Car/V4H SH)
     - Must have at least 16 GB of free space and must support high-speed mode.
   * - Host PC
     - Used for microSD card setup and development environment setup.

       Ubuntu 24.04 with Docker, Windows, or macOS is supported.
   * - SD Card Reader
     - Used for setting up the microSD card.
   * - USB Hub
     - Used to connect a USB keyboard and USB mouse to the board.
   * - USB Keyboard
     - Used to type strings on the terminal of the board.
   * - USB Mouse
     - Used to operate the mouse on the screen of the board.
