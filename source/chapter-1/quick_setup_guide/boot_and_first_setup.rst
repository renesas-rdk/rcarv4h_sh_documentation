Booting the board
^^^^^^^^^^^^^^^^^

At this point the IPL is already written to the board's serial flash ROM
(see :ref:`Flashing the IPL <flashing_the_ipl>`), and the Linux kernel, device tree, and root
filesystem are on the microSD card you flashed above.

Make sure **SW2** is still set to boot from the serial flash ROM, as described in
:ref:`Selection of Boot Device <sh_sw2_boot_device>` — the position you restored after
flashing the IPL.

Insert the microSD card, make sure the Power Control button (the green button near the USB PD port) is in the **OFF** position, connect
the power supply to the board and press the button once so that it latches down to the **ON** position - the board now powers on.

Open a terminal emulator (e.g., **Tera Term**) and connect to the **ChA (HSCIF0)** port of the
board, using the settings listed in :ref:`Serial console channels <sh_serial_console>`:
**921600 bps**, **8N1**, no flow control.

The board will start the boot process.

.. _first_time_boot_setup:

First Boot and Software Setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After powering on the board **for the first time**, perform the following steps:

#. Watch the boot log on the serial console and confirm that Ubuntu boots successfully and
   reaches the login prompt.

#. Log in on the serial console with username **ubuntu** and password **ubuntu**.

#. Connect an Ethernet cable to the board and verify network access:

   .. code-block:: bash

      ping 8.8.8.8 -c 3
      ping bing.com -c 3

   Perform apt update to verify that the board can reach the Ubuntu package repositories:

   .. code-block:: bash

      sudo apt update

#. Resize the root partition to use the full capacity of the microSD card.

   First, check the partition layout:

   .. code-block:: bash

      lsblk

   The root filesystem is the partition mounted at ``/``. Resize it:

   .. code-block:: bash

      sudo apt update
      sudo apt install parted
      sudo parted /dev/mmcblk0 resizepart 1 100%
      sudo resize2fs /dev/mmcblk0p1

   .. note::

      The commands above resize **partition 1** of the microSD card. If ``lsblk`` shows the root
      filesystem on a different partition, change the partition number in both commands.

#. Install ROS 2 Jazzy:

   Install ROS 2 Jazzy on the Cortex-A76 cores (Ubuntu side). You can find and use the provided script here: `apt_install_ros2.sh <https://raw.githubusercontent.com/renesas-rdk/ros2_demo_workspace/refs/heads/main/common_utils/apt_install_ros2.sh>`_.

   Quick installation steps:

   .. code-block:: bash

      wget https://raw.githubusercontent.com/renesas-rdk/ros2_demo_workspace/refs/heads/main/common_utils/apt_install_ros2.sh
      chmod +x apt_install_ros2.sh
      sudo ./apt_install_ros2.sh

   For detailed installation instructions, refer to the official ROS 2 documentation: `ROS 2 Jazzy Installation Guide <https://docs.ros.org/en/jazzy/Installation.html>`_.

#. (Optional) Add the ROS 2 environment setup to ``.bashrc``:

   .. code-block:: bash

      echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
      source ~/.bashrc

This completes the **Quick Start Guide for R-Car V4H SH**.
