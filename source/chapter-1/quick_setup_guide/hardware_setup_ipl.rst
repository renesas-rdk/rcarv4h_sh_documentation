Common hardware setup
^^^^^^^^^^^^^^^^^^^^^

.. caution::

   The power supply for the R-Car V4H SH board must be a USB Power Delivery adapter rated at 65 W or higher.

   The Power Control button (SW1) is a latching (push-push) button, so its physical position tells you
   the state:

   * **OFF** - the button is released and sticks out from the board.
   * **ON** - the button is pressed all the way down and stays latched in that position.

   Before you connect the power supply, make sure the button is in the **OFF** position, that is,
   released and sticking out. Then connect the power supply and press the button once so that it
   latches down to the **ON** position - the board now powers on.
   You should not connect the power supply while the button is in the **ON** position, as this may damage the board.

   Similarly, to power off the board, press the button once so that it pops back out to the **OFF**
   position, and only then remove the power supply. Removing the power supply while the board is
   still powered on may damage the board.


The following image shows the hardware setup for bringing up the board:

.. figure:: ../../images/common_hardware_setup.png
   :alt: Common Hardware Setup
   :width: 700px
   :align: center

   Common Hardware Setup

.. caution::

   The fan must be properly installed before powering on the board.

The setup includes:

- Fan installation
- Power supply connection
- Serial connection for terminal access
- Ethernet connection for network access

.. _flashing_the_ipl:

Flashing the IPL
^^^^^^^^^^^^^^^^

The Initial Program Loader (IPL) is written to the board using the ``ipl-burning`` script from the
:ref:`software package <sh_software_package>`, which drives the board over the serial port from
your host PC.

.. _sh_serial_console:

Serial console channels
"""""""""""""""""""""""

The board has two serial devices. **ChA (HSCIF0)** is the one mainly used, and is the channel
the procedures in this guide connect to:

.. list-table:: Serial Console Channels
   :header-rows: 1
   :widths: 40 20 15 25

   * - **Channel**
     - **Baud rate**
     - **Format**
     - **Flow control**
   * - **ChA (HSCIF0)**

       For example, ``COM<lower num>`` or ``/dev/ttyUSB<lower num>``
     - 921600 bps
     - 8N1
     - none
   * - ChB (HSCIF1)

       For example, ``COM<higher num>`` or ``/dev/ttyUSB<higher num>``
     - 115200 bps
     - 8N1
     - none

.. note::

   Before proceeding, ensure that your machine has the necessary drivers and a terminal emulator (`MobaXterm <https://mobaxterm.mobatek.net/download.html>`_, `Tera Term <https://teratermproject.github.io/index-en.html>`_, etc.) installed.

   For **Windows** users, if the console does not connect, install the appropriate driver.
   The serial communication between the **Windows PC** and **R-Car V4H SH** requires: `FTDI Virtual COM Port (VCP) driver <https://ftdichip.com/drivers/vcp-drivers/>`_

   Download and install the Windows version (``.exe``).

IPL flashing requirements
"""""""""""""""""""""""""

- The software package downloaded and extracted on the host PC.
  See :ref:`Downloading the software package <sh_software_package>`.
- The board connected to the host PC with a **USB-to-microUSB** cable.
- On a **Linux** host PC, ``python3`` and the ``pip`` command installed:

  .. code-block:: bash

     sudo apt-get install python3 python3-pip

- Any other console or terminal emulator that uses the serial port of the board must be
  closed before you run the script. The script cannot open the port while another program
  is holding it.

Procedure
"""""""""

#. Go to the ``ipl-burning`` directory of the extracted software package and run the script.

   On **Linux**:

   .. code-block:: bash

      cd board_setup/ipl-burning
      bash ./run.sh

   On **Windows**, run ``run.bat`` in the ``board_setup\ipl-burning`` directory.

#. Turn off the power and change **SW2** according to the instructions displayed in the console.

#. Press **Enter** to continue.

#. Turn on the power.

#. Wait for the writing process to complete.

#. Turn off the power and change **SW2** again according to the instructions displayed in the console.

#. Press **Enter** to close the program.

.. note::

   Always set the Mode Switch (**SW2**) to the position that ``ipl-burning`` (``run.sh`` or
   ``run.bat``) displays in the console. See
   :ref:`Boot Mode Configuration (DIP Switch) <sh_boot_mode_config>` for the meaning of each
   switch position.

.. note::

   On Linux, the script uses the serial device ``/dev/ttyUSB*``. By default this device cannot
   be accessed by an unprivileged user. Either run the script with ``sudo``, or add your user
   to the ``dialout`` group:

   .. code-block:: bash

      sudo usermod -aG dialout $USER

   Log out and log back in for the group change to take effect.
