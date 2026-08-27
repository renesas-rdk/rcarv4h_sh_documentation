.. _sh_boot_mode_config:

Boot Mode Configuration (DIP Switch)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before powering up the R-Car V4H SH, make sure the board's boot mode is configured correctly
using the Mode Switch (**SW2**). The procedures in the rest of this guide refer back to the
tables in this section whenever they ask you to change a switch position.

SW2 is an 8-position DIP switch. Each position drives one mode pin (MD) of the R-Car V4H SoC:

.. list-table:: SW2 Pin Assignment
   :header-rows: 1
   :widths: 12 15 73

   * - **Pin**
     - **Signal**
     - **Function**
   * - 1
     - MD1
     - Select the boot device.

       See :ref:`Selection of Boot Device <sh_sw2_boot_device>`.
   * - 2
     - MD2
     - See pin 1.
   * - 3
     - MD4
     - See pin 1.
   * - 4
     - MD6
     - Select the master boot processor.

       See :ref:`Selection of Master Boot Processor <sh_sw2_boot_processor>`.
   * - 5
     - \-
     - Not used.
   * - 6
     - MD20
     - Select the JTAG debugging function.

       See :ref:`Selection of JTAG Debugging Functions <sh_sw2_jtag>`.
   * - 7
     - MD21
     - See pin 6.
   * - 8
     - MD10
     - See pin 6.

Each position sets the electrical condition of its mode pin:

.. list-table:: SW2 Electrical Condition
   :header-rows: 1
   :widths: 20 80

   * - **Position**
     - **Electrical condition**
   * - ON
     - Pull-down to GND
   * - OFF
     - Pull-up to 3.3 V

.. _sh_sw2_boot_device:

Selection of Boot Device
""""""""""""""""""""""""

Pins 1, 2, and 3 (**MD1**, **MD2**, **MD4**) select the boot device of the R-Car V4H SH board:

.. list-table:: Selection of Boot Device
   :header-rows: 1
   :widths: 13 13 13 61

   * - **Pin 1 (MD1)**
     - **Pin 2 (MD2)**
     - **Pin 3 (MD4)**
     - **Boot device**
   * - **ON**
     - **ON**
     - **ON**
     - Serial flash ROM, single reading at 40 MHz with the use of DMA (default)
   * - OFF
     - OFF
     - OFF
     - HSCIF downloading mode, 921,600 bps

.. note::

   Any combination other than those listed above is not supported.

.. _sh_sw2_boot_processor:

Selection of Master Boot Processor
""""""""""""""""""""""""""""""""""

Pin 4 (**MD6**) selects the master boot processor of the R-Car V4H SH board:

.. list-table:: Selection of Master Boot Processor
   :header-rows: 1
   :widths: 20 80

   * - **Pin 4 (MD6)**
     - **Master boot processor**
   * - **OFF**
     - Booted through Cortex-R52 (default)
   * - ON
     - Booted through ICUMXA

.. _sh_sw2_jtag:

Selection of JTAG Debugging Functions
"""""""""""""""""""""""""""""""""""""

The JTAG functions on **CN3** are determined by the combination of pins 6, 7, and 8
(**MD20**, **MD21**, **MD10**):

.. list-table:: Selection of JTAG Debugging Functions
   :header-rows: 1
   :widths: 15 15 15 55

   * - **Pin 6 (MD20)**
     - **Pin 7 (MD21)**
     - **Pin 8 (MD10)**
     - **JTAG (CN3)**
   * - **ON**
     - **ON**
     - **ON**
     - \- (initial default)
   * - OFF
     - ON
     - ON
     - ICUMX JTAG
   * - ON
     - OFF
     - ON
     - CoreSight
   * - OFF
     - ON
     - OFF
     - ICUMX LPD

.. note::

   Any combination other than those listed above is reserved.

.. caution::

   Always power off the board before changing the SW2 settings.
