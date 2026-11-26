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

Installing the AI Runtime Libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. important::

   **Required for all AI applications.** The Ubuntu image does not include the HyCo TVM runtime
   (``libtvm_runtime.so``) or ONNX Runtime (``libonnxruntime.so``). Without them, the AI sample
   applications and any application that runs a neural network model on the board **do not
   run**. Complete this section before you run or build an AI application.

You build the ``libv4h-ai-sdk-dev`` package yourself from two downloads with the
``make-v4h-ai-dev-deb.sh`` script, and install it on the board.

.. note::

   The package does not include the R-Car xOS headers and libraries (``rcar-xos``, ``vsfwk``,
   ``osal_configuration``, ``lib*.a``).

#. Download the two input files on your host PC:

   .. list-table::
      :header-rows: 1
      :widths: 30 35 35

      * - **File**
        - **Name**
        - **Where to get it**
      * - AI SDK for Sparrow Hawk
        - ``ai_sdk-v*.zip`` (for example ``ai_sdk-v2026-11-05.zip``)
        - Renesas Secure Portal
      * - ONNX Runtime for Linux aarch64
        - ``onnxruntime-linux-aarch64-*.tgz``
        - `ONNX Runtime v1.17.1 on GitHub <https://github.com/microsoft/onnxruntime/releases/download/v1.17.1/onnxruntime-linux-aarch64-1.17.1.tgz>`_

   Keep the files as they are: do not rename or extract them.

#. Get the build script on your host PC. The script is in the ``ros2_demo_workspace``
   repository on the Renesas Partner GitLab. Clone the repository and check out the
   ``feat-librcar-xos-scripts`` branch:

   .. code-block:: bash

      git clone https://partnergitlab.renesas.solutions/pai/ros2/utility/ros2_demo_workspace.git
      cd ros2_demo_workspace
      git checkout feat-librcar-xos-scripts

#. Build the package. Choose **one** of the two options below.

   **Option A: build on the host PC**

   Use a Linux host PC, such as Ubuntu 24.04 (x86_64). The build takes a few seconds. Put the two
   input files and the script in one directory, for example ``~/v4h-ai-deb``:

   .. code-block:: bash

      sudo apt install unzip
      mkdir -p ~/v4h-ai-deb
      cp <path to ros2_demo_workspace>/common_utils/make-v4h-ai-dev-deb.sh ~/v4h-ai-deb/
      cd ~/v4h-ai-deb
      ls

   The directory now holds the three files:

   .. code-block:: console

      ai_sdk-v2026-11-05.zip  make-v4h-ai-dev-deb.sh  onnxruntime-linux-aarch64-1.17.1.tgz

   Run the script:

   .. code-block:: bash

      bash make-v4h-ai-dev-deb.sh

   Copy the package to the board:

   .. code-block:: bash

      scp libv4h-ai-sdk-dev_3.47.0-1_arm64.deb ubuntu@<board IP address>:~/

   **Option B: build on the board**

   Use this option if you do not have a Linux host PC. The build takes about 30 seconds. Copy the
   two input files and the script from the host PC to the board. Run the ``scp`` command in the
   directory that holds the two input files:

   .. code-block:: bash

      ssh ubuntu@<board IP address> mkdir -p v4h-ai-deb
      scp ai_sdk-v2026-11-05.zip onnxruntime-linux-aarch64-1.17.1.tgz <path to ros2_demo_workspace>/common_utils/make-v4h-ai-dev-deb.sh ubuntu@<board IP address>:~/v4h-ai-deb/

   Then, on the board, go to the directory:

   .. code-block:: bash

      sudo apt install unzip
      cd ~/v4h-ai-deb
      ls

   The directory now holds the three files:

   .. code-block:: console

      ai_sdk-v2026-11-05.zip  make-v4h-ai-dev-deb.sh  onnxruntime-linux-aarch64-1.17.1.tgz

   Run the script:

   .. code-block:: bash

      bash make-v4h-ai-dev-deb.sh

   With either option, the script finds the two files in the current directory and writes the
   package there:

   .. code-block:: console

      [INFO] inputs: ai_sdk-v2026-11-05.zip, onnxruntime-linux-aarch64-1.17.1.tgz
      [INFO] built /home/ubuntu/v4h-ai-deb/libv4h-ai-sdk-dev_3.47.0-1_arm64.deb (SDK 3.47.0, TVM 1.0.6, ONNX Runtime 1.17.1)
      [INFO] on the board: sudo dpkg -i libv4h-ai-sdk-dev_3.47.0-1_arm64.deb

   The version in the package name (``3.47.0``) is the R-Car xOS version of the AI SDK, and
   ``-1`` is the package revision. If a file is missing, or more than one file matches, the
   script names it and stops.

#. On the board, go to the directory that holds the package (``~`` for Option A, ``~/v4h-ai-deb``
   for Option B) and install it:

   .. code-block:: bash

      sudo dpkg -i libv4h-ai-sdk-dev_3.47.0-1_arm64.deb

   Use the name of the ``.deb`` file you built.

#. Check that the libraries are installed:

   .. code-block:: bash

      ldconfig -p | grep -E 'libtvm_runtime|libonnxruntime'

   The output lists ``libtvm_runtime.so``, ``libonnxruntime.so`` and ``libonnxruntime.so.1.17.1``.

The package installs:

- ``libtvm_runtime.so`` and ``libonnxruntime.so*`` in ``/usr/lib/aarch64-linux-gnu``
- the ONNX Runtime headers in ``/usr/include``
- the license files in ``/usr/share/doc/libv4h-ai-sdk-dev``

.. note::

   If the board has the older ``librcar-xos-v4h-dev`` package, ``libv4h-ai-sdk-dev`` takes over
   its HyCo TVM runtime and ONNX Runtime files. To reinstall or upgrade the older package, remove
   ``libv4h-ai-sdk-dev`` first.

This completes the **Quick Start Guide for R-Car V4H SH**.
