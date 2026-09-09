Communication Interfaces
^^^^^^^^^^^^^^^^^^^^^^^^

This section provides usage examples of the communication interfaces available on the R-Car V4H SH.

.. _can_interface:

CAN-FD x2
"""""""""

The R-Car V4H SH is equipped with two CAN-FD (Controller Area Network Flexible Data-Rate) ports that enable high-speed communication for automotive and industrial applications.

.. tip::

   The R-Car V4H SH is equipped with an onboard CAN transceiver (``MCP2558FDT-H_MNY``) and an integrated **120 Ω termination resistor**, eliminating the need for any external CAN transceiver circuitry.

Connect the CAN-FD ports to your CAN network using appropriate cables, matching the CAN-H and CAN-L lines of each port.

Both CAN-FD ports are brought out on a single 6-pin header, labeled ``CAN BUS CN``
on the board (schematic reference ``CONN2``). **CAN0 is on the even-numbered pins
and CAN1 is on the odd-numbered pins**, with both ports sharing the same ground.

The figure below shows that header twice, so that the schematic pin numbers can be
matched to the physical connector:

- **Top — schematic view.** The ``CAN BUS CN`` symbol taken from the board schematic,
  showing which signal is routed to each of the six pins.
- **Bottom — photo of the board.** The same header as it appears on the
  R-Car V4H SH, with every pin labeled. Red labels are the CAN0 signals,
  blue labels are the CAN1 signals.

.. figure:: ../../images/can_fd.png
   :alt: CAN BUS CN header of the R-Car V4H SH, shown as a schematic symbol above and as a labeled board photo below
   :align: center
   :width: 500px

   ``CAN BUS CN`` (CONN2) header — schematic symbol (top) and the corresponding
   pins on the board (bottom).

.. important::

   Use the ``2`` printed on the silkscreen next to the header (highlighted in red in
   the photo) to orient the connector: it marks **pin 2**. With the board silkscreen
   text upright, the left column of pins is **CAN0** and the right column is **CAN1**.

.. list-table:: CAN BUS CN (CONN2) Pinout
   :header-rows: 1
   :widths: 15 25 60

   * - Pin
     - Signal
     - Description
   * - 1
     - CAN1_L
     - CAN1 bus line — low.
   * - 2
     - CAN0_L
     - CAN0 bus line — low. Marked by the ``2`` on the silkscreen.
   * - 3
     - GND
     - Common ground, shared by both ports.
   * - 4
     - GND
     - Common ground, shared by both ports.
   * - 5
     - CAN1_H
     - CAN1 bus line — high.
   * - 6
     - CAN0_H
     - CAN0 bus line — high.

Follow the steps below to use the CAN-FD interfaces on the R-Car V4H SH running Ubuntu.

This example covers CAN-FD frames only; it does not cover the configuration of Classic CAN frames.

Verify that the CAN interfaces are recognized:

.. code-block:: bash

   ip link show | grep can

Example output:

.. code-block:: console

   5: can0: <NOARP,ECHO> mtu 72 qdisc noop state DOWN mode DEFAULT group default qlen 10 link/can
   6: can1: <NOARP,ECHO> mtu 72 qdisc noop state DOWN mode DEFAULT group default qlen 10 link/can

Bring up the CAN0 and CAN1 interfaces (for example, 1 Mbps nominal, 5 Mbps data):

.. code-block:: bash

   # Configure and bring up the CAN0 interface with the specified bitrate and data bitrate for CAN-FD
   sudo ip link set can0 down
   sudo ip link set can0 type can restart-ms 100 bitrate 1000000 dbitrate 5000000 fd on
   sudo ip link set can0 up

   # Configure and bring up the CAN1 interface with the specified bitrate and data bitrate for CAN-FD
   sudo ip link set can1 down
   sudo ip link set can1 type can restart-ms 100 bitrate 1000000 dbitrate 5000000 fd on
   sudo ip link set can1 up

Check the interface status:

.. code-block:: bash

   ip -details link show can0
   ip -details link show can1

Send and receive CAN messages:

You can use the ``can-utils`` package for testing CAN-FD communication.

#. Install ``can-utils`` if it is not already installed:

   .. code-block:: bash

      sudo apt install can-utils

#. Connect the CAN0_H to CAN1_H and CAN0_L to CAN1_L.

#. In one terminal, listen for incoming CAN-FD frames:

   .. code-block:: bash

      candump can0

#. In another terminal, send a test frame:

   .. code-block:: bash

      cansend can1 123##01122334455667788

RasPi GPIO 40-pin Header
""""""""""""""""""""""""

The Raspberry Pi GPIO 40-pin header on the R-Car V4H SH provides a versatile interface for connecting various peripherals and expansion boards compatible with the Raspberry Pi pin layout. This header includes multiple communication protocols such as I2C, UART, GPIO, PCM, and PWM.

The following communication protocols are supported:

- I2C (Inter-Integrated Circuit)
- UART (Universal Asynchronous Receiver/Transmitter)
- GPIO (General Purpose Input/Output)
- PCM (Pulse Code Modulation)
- PWM (Pulse Width Modulation)

Pin Out Diagram
~~~~~~~~~~~~~~~

.. figure:: ../../images/GPIO_pin.png
   :alt: R-Car V4H SH Raspberry Pi GPIO 40-pin Header Pin Out
   :align: center
   :width: 600px

   R-Car V4H SH Raspberry Pi GPIO 40-pin Header Pin Out

I2C (Inter-Integrated Circuit)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The I2C interface allows communication with multiple slave devices using just two wires: SDA (data line) and SCL (clock line).

It is commonly used for connecting sensors, displays, and other peripherals.

On the R-Car V4H SH, the I2C pins are located on the Raspberry Pi GPIO 40-pin header as follows:

.. list-table:: I2C3 Interface Pins
   :header-rows: 1
   :widths: 25 25 50

   * - Pin Name
     - Function
     - Description
   * - GPIO2 — pin 3
     - I2C3 SDA3
     - I2C3 data line, serial data (connected with a 4.7 kΩ pull-up resistor).
   * - GPIO3 — pin 5
     - I2C3 SCL3
     - I2C3 clock line, serial clock (connected with a 4.7 kΩ pull-up resistor).

**Usage example with i2c-tools**

First, install the ``i2c-tools`` package if it is not already installed:

.. code-block:: bash

   sudo apt install i2c-tools

List all I2C buses available on the system:

.. code-block:: bash

   i2cdetect -l

Example output:

.. code-block:: console

   i2c-0   i2c             e6500000.i2c                            I2C adapter
   i2c-3   i2c             e66d0000.i2c                            I2C adapter
   i2c-4   i2c             e66d8000.i2c                            I2C adapter
   i2c-6   i2c             i2c-0-mux (chan_id 0)                   I2C adapter
   i2c-7   i2c             i2c-0-mux (chan_id 1)                   I2C adapter
   i2c-8   i2c             i2c-0-mux (chan_id 2)                   I2C adapter
   i2c-9   i2c             i2c-0-mux (chan_id 3)                   I2C adapter
   i2c-10  i2c             ti-sn65dsi86-aux                        I2C adapter

Find the correct bus number for I2C3:

.. code-block:: bash

   ls -l /sys/class/i2c-dev/

Example output:

.. code-block:: console

   total 0
   lrwxrwxrwx 1 root root 0 Jul 28 15:04 i2c-0 -> ../../devices/platform/soc/e6500000.i2c/i2c-0/i2c-dev/i2c-0
   lrwxrwxrwx 1 root root 0 Jul 28 15:04 i2c-10 -> ../../devices/platform/soc/e6500000.i2c/i2c-0/i2c-6/6-002c/ti_sn65dsi86.aux.6188/i2c-10/i2c-dev/i2c-10
   lrwxrwxrwx 1 root root 0 Jul 28 15:04 i2c-3 -> ../../devices/platform/soc/e66d0000.i2c/i2c-3/i2c-dev/i2c-3
   lrwxrwxrwx 1 root root 0 Jul 28 15:04 i2c-4 -> ../../devices/platform/soc/e66d8000.i2c/i2c-4/i2c-dev/i2c-4
   lrwxrwxrwx 1 root root 0 Jul 28 15:04 i2c-6 -> ../../devices/platform/soc/e6500000.i2c/i2c-0/i2c-6/i2c-dev/i2c-6
   lrwxrwxrwx 1 root root 0 Jul 28 15:04 i2c-7 -> ../../devices/platform/soc/e6500000.i2c/i2c-0/i2c-7/i2c-dev/i2c-7
   lrwxrwxrwx 1 root root 0 Jul 28 15:04 i2c-8 -> ../../devices/platform/soc/e6500000.i2c/i2c-0/i2c-8/i2c-dev/i2c-8
   lrwxrwxrwx 1 root root 0 Jul 28 15:04 i2c-9 -> ../../devices/platform/soc/e6500000.i2c/i2c-0/i2c-9/i2c-dev/i2c-9

In this example, I2C3 corresponds to bus number 3.

.. note::

   *How to identify the correct I2C bus number for I2C3?*

   You can identify the correct I2C bus number by checking the device tree source (DTS) file for the R-Car V4H SH or by referring to the system documentation.

   In this case, the device tree of the R-Car V4H SH defines the I2C3 interface as ``e66d0000.i2c``, which is mapped to **I2C bus number 3**.

Scan for I2C devices on bus 3:

.. code-block:: bash

   sudo i2cdetect -y 3

Example output:

.. code-block:: console

        0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
   00:                         -- -- -- -- -- -- -- --
   10: -- -- -- -- -- -- -- -- -- -- 1a -- -- -- -- --
   20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   70: -- -- -- -- -- -- -- --

The above output indicates that a device with address ``0x1a`` is connected to the I2C3 bus. In this case, it is the Argon40 fan.

Use the ``i2cset`` command to write the duty-cycle register (``0x80``) of the Argon40 Fan HAT.
The value is a percentage between 0 and 100:

.. code-block:: bash

   sudo i2cset -y 3 0x1a 0x80 0     # 0%
   sudo i2cset -y 3 0x1a 0x80 50    # 50%
   sudo i2cset -y 3 0x1a 0x80 100   # 100%

.. note::

   These raw writes work only while no fan device tree overlay is loaded, which is the case in
   the ``i2cdetect`` output above: address ``1a`` is listed rather than ``UU``. When the
   ``#fan-argon40`` overlay is applied, the kernel driver claims ``0x1a`` and ``i2cset`` refuses
   to touch it. Control the fan through hwmon instead:

   .. code-block:: bash

      echo 2 | sudo tee /sys/devices/platform/pwm-fan-ext/hwmon/hwmon0/pwm1_enable
      echo 101 | sudo tee /sys/devices/platform/pwm-fan-ext/hwmon/hwmon0/pwm1   # 0..255

UART (Universal Asynchronous Receiver/Transmitter)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The UART interface provides serial communication capabilities, allowing data exchange between the R-Car V4H SH and other devices such as micro-controllers, GPS modules, or serial consoles.

On the R-Car V4H SH, the UART pins are located on the Raspberry Pi GPIO 40-pin header as follows:

.. list-table:: UART Interface Pins
   :header-rows: 1
   :widths: 25 25 50

   * - Pin Name
     - Function
     - Description
   * - GPIO14 — pin 8
     - TXD
     - UART transmit data (TX) signal.
   * - GPIO15 — pin 10
     - RXD
     - UART receive data (RX) signal.

**Usage example with minicom**

First, connect the UART header pins to a USB-UART adapter to establish a serial connection with a host computer; on the host PC, the adapter appears as ``/dev/ttyUSB0``.

Install the ``minicom`` package if it is not already installed:

.. code-block:: bash

   sudo apt install minicom

List available serial ports:

.. code-block:: bash

   # Run on the R-Car V4H SH
   ls /dev/ttySC*

The output should show the available serial ports, including the UART interface:

.. code-block:: console

   /dev/ttySC0  /dev/ttySC1  /dev/ttySC2

``ttySC0`` and ``ttySC1`` are the CN4 debug console channels; ``ttySC2`` is the 40-pin header
UART on GPIO14/GPIO15.

Open a serial connection using ``minicom``:

.. code-block:: bash

   # Run on the R-Car V4H SH
   sudo minicom -D /dev/ttySC2 -b 115200

On the host PC, open a second minicom session on the USB-UART adapter:

.. code-block:: bash

   # Run on the host PC
   sudo minicom -D /dev/ttyUSB0 -b 115200

In each session, enable echoing of typed characters with ``Ctrl-A`` then ``E``, and press
``Ctrl-A`` then ``U`` to add a carriage return (CR) to each incoming linefeed (LF). Characters
typed in either session now appear in the other, which confirms the 40-pin header UART works in
both directions.

GPIO (General Purpose Input/Output)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The GPIO pins allow digital input and output operations, enabling interaction with various sensors, actuators, and other electronic components.

Refer to the R-Car V4H SH GPIO pinout documentation for detailed information on each GPIO pin's capabilities and functions.

**Usage example with gpiod**

First, install the ``gpiod`` package if it is not already installed:

.. code-block:: bash

   sudo apt install gpiod

List available GPIO chips:

.. code-block:: bash

   gpiodetect

List lines for a specific GPIO chip (for example, ``gpiochip1``):

.. code-block:: bash

   gpioinfo gpiochip1

.. _audio_interface:

Audio Interface
"""""""""""""""

The audio interface is used for audio data transmission, allowing the R-Car V4H SH to connect with audio codecs and other audio peripherals.

The R-Car V4H SH has two audio input ports. These signals are mixed on the IC and therefore handled as a single-channel input on the board.

- Hardware setup:

  #. Connect headset/earphone/Speaker to CONN3.
  #. (If possible) Connect audio output like a smartphone to CONN4.

- Software setup:

  #. Install ``alsa-utils`` package if it is not already installed:

     .. code-block:: bash

        sudo apt install alsa-utils

  #. Set the audio output to the headphone jack (CONN3) using the following script:

     .. code-block:: bash

        #!/bin/bash
        C="-c 0"

        amixer $C set "Headphone" on
        amixer $C set "Headphone" 40%
        amixer $C set "Mixout Left DAC Left" on
        amixer $C set "Mixout Right DAC Right" on
        amixer $C set "Aux" on
        amixer $C set "Aux" 80%
        amixer $C set "Mixin PGA" on
        amixer $C set "Mixin PGA" 50%
        amixer $C set "ADC" on
        amixer $C set "ADC" 80%
        amixer $C set "Mixin Left Aux Left" on
        amixer $C set "Mixin Right Aux Right" on
        amixer $C set "Mic 1" on
        amixer $C set "Mic 1" 80%
        amixer $C set "Mixin Left Mic 1" on
        amixer $C set "Mixin Right Mic 1" on

     Save the script as ``audio_setup.sh``, make it executable with ``chmod +x audio_setup.sh``, and run it with ``./audio_setup.sh`` to configure the audio output.

**Usage example with alsa-utils**

Only playback test:

.. code-block:: bash

   speaker-test -c 2 -l 3 -t wav -W /usr/share/sounds/alsa/

Only recording test:

.. code-block:: bash

   arecord -D hw:0,0 -t wav -d 5 -c 2 -r 48000 -f S16_LE audio.wav
