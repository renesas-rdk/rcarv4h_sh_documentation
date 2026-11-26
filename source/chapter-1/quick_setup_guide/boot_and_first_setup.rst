.. _sh_booting_the_board:

Booting the Board
^^^^^^^^^^^^^^^^^

At this point the IPL is already written to the board's serial flash ROM
(see :ref:`Flashing the IPL <flashing_the_ipl>`), and the Linux kernel, device tree, and root
filesystem are on the microSD card you flashed above.

Make sure **SW2** is still set to boot from the serial flash ROM, as described in
:ref:`Selection of Boot Device <sh_sw2_boot_device>` — the position you restored after
flashing the IPL.

Insert the microSD card, make sure the Power Control button (the green button near the USB PD port) is in the **OFF** position, connect
the power supply to the board and press the button once so that it latches down to the **ON** position — the board now powers on.

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

      ping -c 3 8.8.8.8
      ping -c 3 bing.com

   Then run ``apt update`` to verify that the board can reach the Ubuntu package repositories:

   .. code-block:: bash

      sudo apt update

#. Resize the root partition to use the full capacity of the microSD card.

   First, check the partition layout:

   .. code-block:: bash

      lsblk

   The root filesystem is the partition mounted at ``/``. Resize it:

   .. code-block:: bash

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

.. _sh_ai_runtime_package:

Installing the R-Car V4H AI SDK
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. important::

   **Required for all AI applications.** The Ubuntu image does not include the HyCo TVM runtime
   (``libtvm_runtime.so``) or ONNX Runtime (``libonnxruntime.so``). Without them, the AI sample
   applications and any application that runs a neural network model on the board **do not
   run**. Complete this section before you run or build an AI application.

You build the ``libv4h-ai-sdk-dev`` package on a Linux host PC with the
``make-v4h-ai-dev-deb.sh`` script, and install it on the board. The script downloads ONNX Runtime
itself, so you only download the AI SDK.

#. On a Linux host PC, such as Ubuntu 24.04 (x86_64), create a working directory:

   .. code-block:: bash

      sudo apt install curl unzip
      mkdir -p ~/v4h-ai-deb
      cd ~/v4h-ai-deb

#. Download the R-Car V4H AI SDK for Sparrow Hawk (``ai_sdk-v*.zip``, for example
   ``ai_sdk-v2026-11-05.zip``) from the Renesas Secure Portal into ``~/v4h-ai-deb``.

   Keep the file as it is: do not rename or extract it.

#. Get the build script. You can find it here:
   `make-v4h-ai-dev-deb.sh <https://raw.githubusercontent.com/renesas-rdk/ros2_demo_workspace/refs/heads/main/common_utils/make-v4h-ai-dev-deb.sh>`_.

   .. code-block:: bash

      wget https://raw.githubusercontent.com/renesas-rdk/ros2_demo_workspace/refs/heads/main/common_utils/make-v4h-ai-dev-deb.sh

#. Check that the directory holds the two files:

   .. code-block:: bash

      ls

   .. code-block:: console

      ai_sdk-v2026-11-05.zip  make-v4h-ai-dev-deb.sh

#. Build the package. The host PC needs internet access, because the script downloads ONNX
   Runtime 1.17.1 for Linux arm64 from the official Microsoft NuGet package:

   .. code-block:: bash

      bash make-v4h-ai-dev-deb.sh

   The script finds the AI SDK in the current directory and writes the package there:

   .. code-block:: console

      [INFO] input: ai_sdk-v2026-11-05.zip
      [INFO] downloading ONNX Runtime 1.17.1: https://www.nuget.org/api/v2/package/Microsoft.ML.OnnxRuntime/1.17.1
      [INFO] built /home/ubuntu/v4h-ai-deb/libv4h-ai-sdk-dev_3.47.0-1_arm64.deb (SDK 3.47.0, TVM 1.0.6, ONNX Runtime 1.17.1)
      [INFO] on the board: sudo dpkg -i libv4h-ai-sdk-dev_3.47.0-1_arm64.deb

   The version in the package name (``3.47.0``) is the version of the R-Car V4H AI SDK, and ``-1``
   is the package revision. If the AI SDK file is missing, or more than one file matches, the script names
   it and stops.

#. Copy the package to the board:

   .. code-block:: bash

      scp libv4h-ai-sdk-dev_3.47.0-1_arm64.deb ubuntu@<board IP address>:~/

   Use the name of the ``.deb`` file you built.

#. On the board, install the package:

   .. code-block:: bash

      cd ~
      sudo dpkg -i libv4h-ai-sdk-dev_3.47.0-1_arm64.deb

#. Check that the libraries are installed:

   .. code-block:: bash

      ldconfig -p | grep -E 'libtvm_runtime|libonnxruntime'

   The output lists ``libtvm_runtime.so``, ``libonnxruntime.so`` and ``libonnxruntime.so.1.17.1``.

The package installs:

- ``libtvm_runtime.so`` and ``libonnxruntime.so*`` in ``/usr/lib/aarch64-linux-gnu``
- the ONNX Runtime headers in ``/usr/include``
- the license files in ``/usr/share/doc/libv4h-ai-sdk-dev``

This completes the **Quick Start Guide for R-Car V4H SH**.
