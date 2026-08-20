Ubuntu System with R-Car/V4H SH
-------------------------------

This section provides usage information about the interfaces available on the R-Car/V4H SH when running the Ubuntu system.

For more details about specification of each interface, refer to the `Sparrow Hawk Hardware User's Manual <https://drive.google.com/file/d/1lqiRE7t8C6GWOmuj0PKMItuj-R3VaYD1/view>`_.

Overview
^^^^^^^^
The R-Car/V4H SH supports multiple peripheral interfaces that allow users to connect and control external devices for various robotic and industrial applications.
These interfaces include:

.. figure:: ../../images/hardware_interface.png
   :alt: R-Car/V4H Sparrow Hawk Hardware Interfaces
   :align: center
   :width: 800px

   R-Car/V4H Sparrow Hawk Hardware Interfaces

Main Interfaces
^^^^^^^^^^^^^^^

The main interfaces available on the R-Car/V4H SH are listed below.

.. list-table:: Main Interfaces
   :header-rows: 1
   :widths: 25 25 50

   * - Interface
     - Connector
     - Description
   * - Camera I/F
     - J1, J2
     - 2x MIPI CSI camera
   * - Display
     - CN6, J4
     - 1x DP, 1x DSI
   * - Ethernet AVB
     - CN2
     - 1 port (1 Gbps)
   * - Debug Serial
     - CN4
     - 2 ports
   * - Audio
     - CONN3, CONN4
     - In/Out, In
   * - PCIe 4.0
     - CN5
     - 1x M.2 Key-M (x2 lane)
   * - USB 3.0
     - USB4, USB5, USB6
     - 2x USB Type-A, 2x USB Type-C
   * - CAN-FD
     - CONN2
     - 2 ports
   * - PWM
     - J3
     - 1 port
   * - JTAG
     - CN3
     - 1 port
   * - Removable Media
     - CN1
     - 1x microSD
   * - Extensions
     - CN7
     - Raspberry Pi® 40-pin GPIO header
   * - Mode Switches
     - SW2
     - DIP switch
   * - Power
     - USB1 (input)
     - USB PD 20 V
   * - Power Control
     - SW1, SW3, CONN1
     - 2x switch, 1x jumper

Each subsection provides details on how to identify, configure, and access these interfaces within the Ubuntu environment.

.. toctree::
    :hidden:
    :maxdepth: 2

    high_speed_interfaces
    communication_interface
    other_interfaces
