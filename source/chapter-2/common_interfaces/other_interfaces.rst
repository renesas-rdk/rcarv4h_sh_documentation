Other interfaces
^^^^^^^^^^^^^^^^

The R-Car V4H SH is equipped with several additional interfaces to enhance its functionality and connectivity options.

This section provides an overview of these interfaces, including DisplayPort, DSI, USB-UART, and JTAG.

DisplayPort
"""""""""""

The R-Car V4H SH features a DisplayPort interface (**CN6**) for video output to an external display.
To use this interface, connect a DisplayPort cable from the board to a compatible monitor.

The DisplayPort interface also supports audio output, allowing you to transmit both video and audio signals through the same connection.

This is particularly useful for multimedia applications.

.. seealso::

   For running the graphical desktop environment on a DisplayPort monitor, see :ref:`ubuntu_desktop`.

DSI 
"""

The R-Car V4H SH includes a DSI interface (**J4**) for connecting to compatible displays.

This interface is commonly used for high-resolution displays and touchscreens, providing a direct connection to the display panel.

The following displays/adapters are supported:

- `Waveshare 13.3 MIPI DSI panel <https://www.waveshare.com/13.3inch-dsi-lcd.htm>`_
- `RPi Display 2 5" MIPI DSI panel <https://www.raspberrypi.com/products/touch-display-2/>`_
- `RPi Display 2 7" MIPI DSI panel <https://www.raspberrypi.com/products/touch-display-2/>`_
- `Olimex MIPI-HDMI adapter <https://www.olimex.com/Products/IoT/ESP32-P4/MIPI-HDMI/open-source-hardware>`_

.. _usb_uart:

USB-UART
""""""""

The R-Car V4H SH includes a USB-UART interface (**CN4**) for serial communication and debugging purposes.
This interface allows you to connect the board to a host computer via a USB cable and access the serial console.

The single USB connection exposes two serial channels on the host computer.
On Linux they appear as ``/dev/ttyUSB<n>``, and on Windows as ``COM<n>``:

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

**ChA (HSCIF0)** is the main console channel and carries the boot log and the Linux login prompt.
It is always the device with the **lower** number of the two, because both channels are enumerated
from the same USB device.

The format **8N1** means 8 data bits, no parity, and 1 stop bit.

We recommend using a terminal emulator such as ``minicom`` (Linux) or
`Tera Term <https://teratermproject.github.io/index-en.html>`_ (Windows) to connect to the USB-UART interface.

For example, to open the main console with ``minicom`` on a Linux host:

.. code-block:: bash

   sudo minicom -D /dev/ttyUSB0 -b 921600

.. note::

   For **Windows** users, if the console does not connect, install the
   `FTDI Virtual COM Port (VCP) driver <https://ftdichip.com/drivers/vcp-drivers/>`_.

.. seealso::

   For the full serial console setup procedure, see :ref:`sh_serial_console`.

JTAG
""""

The R-Car V4H SH provides a JTAG interface (**CN3**) for debugging and programming the three
Arm® Cortex®-R52 (CR52) cores.

This interface allows developers to perform low-level debugging, firmware updates, and system
analysis, which is essential for development in Multi-Core applications.

The JTAG function exposed on **CN3** depends on the SW2 switch configuration.
See :ref:`Selection of JTAG Debugging Functions <sh_sw2_jtag>`.

.. seealso::

   `Sparrow Hawk Zephyr support <https://docs.zephyrproject.org/latest/boards/retronix/sparrowhawk_rcar_v4h/doc/sparrow_hawk_rcar_v4h_r52.html>`_
