.. _reaction_setup:

REACTION Setup
""""""""""""""

This page collects everything that has to be installed once, on the host machine and on
the target board, before REACTION can compile and evaluate models.

Software Requirements
~~~~~~~~~~~~~~~~~~~~~

To use REACTION, the following software requirements must be met:

- A Linux host machine with Ubuntu 20.04 or higher. On Windows machines it is necessary to use
  the Windows Subsystem for Linux (WSL2).

- ``sshpass`` on the host machine. The setup scripts of the following sections use it to reach
  the board over SSH:

  .. code-block:: bash

     sudo apt install sshpass

- The HyCo and SDK packages listed below, downloaded from the Renesas Secure Portal.

The packages are available from `(Gen4) R-Car V4x SW
<https://www.renesas.com/en/myrenesas/secure-portals/gen4-r-car-v4x-sw>`_. This is a secure
portal, so an account and an approved access request for the R-Car V4x SW package are required
before the following packages can be downloaded:

.. note::

   ``v3.xx.0`` stands for the SDK release being installed; take all four packages from the same
   release. These pages were written against ``v3.43.0``. Substitute that number wherever
   ``v3.xx.0`` appears in a package name or a path on these pages.

.. list-table:: HyCo / SDK Packages
   :header-rows: 1
   :widths: 30 70

   * - Package Name
     - Package Description
   * - [HyCo] Hybrid Compiler

       (SDK v3.xx.0)
     - Hybrid Compiler SDK Addon to compile and run neural networks in RCG4
   * - [HyCo] Installation Scripts for Hybrid Compiler

       (SDK v3.xx.0)
     - Installation scripts helping to set up Hybrid Compiler and its environment.

       These may become part of Hybrid Compiler package in future releases.
   * - [HyCo] ONNX Models for Hybrid Compiler

       (SDK v3.xx.0)
     - ONNX files of HyCo sample networks including the "app" samples
   * - [SDK] SDK1 installer for Linux PC

       (SDK v3.xx.0)
     - Installer for xOS SDK 1 for Linux

Detailed Steps
~~~~~~~~~~~~~~

.. note::

   The R-Car V4H SH runs Ubuntu 24.04, while the original guide covers Yocto Linux. The
   following steps are based on that guide, adapted for Ubuntu 24.04.

#. Unpack **[HyCo] Installation Scripts for Hybrid Compiler**

#. Read the **Installation_ReadMe.md** to understand the installation process for the Hybrid
   Compiler and its environment.

#. Change the ``installation/default_settings.sh`` file (available after extracting the
   installation scripts package) as follows:

   .. list-table:: Environment Variable Configuration
      :header-rows: 1
      :widths: 26 12 12 50

      * - Variable
        - Default
        - Modified
        - Description
      * - ``INSTALL_CEVA_CSL``
        - ``1``
        - ``0``
        - The CEVA DSP is not supported in this release on the R-Car V4H SH platform, so the
          automatic CEVA CSL installation is skipped.
      * - ``INSTALL_CEVA_DSP``
        - ``1``
        - ``0``
        - The CEVA DSP is not supported in this release on the R-Car V4H SH platform, so the
          automatic CEVA DSP installation is skipped.
      * - ``INSTALL_PY310_ON_BOARD``
        - ``1``
        - ``0``
        - Skip the automatic Python 3.10 installation on the target board. It is installed
          manually afterwards.
      * - ``INSTALL_RPC``
        - ``1``
        - ``0``
        - Skip the automatic RPC installation on the target board. It is installed manually
          afterwards.

   The following commands can be used to modify the file:

   .. code-block:: bash

      # Change to the directory of the extracted installation scripts package first,
      # then run the following commands:
      cd installation

      # Change the DSP and CEVA CSL installation settings to 0
      sed -i 's/INSTALL_CEVA_CSL=1/INSTALL_CEVA_CSL=0/' default_settings.sh
      sed -i 's/INSTALL_CEVA_DSP=1/INSTALL_CEVA_DSP=0/' default_settings.sh

      # Change the Python 3.10 and RPC installation settings to 0
      sed -i 's/INSTALL_PY310_ON_BOARD=1/INSTALL_PY310_ON_BOARD=0/' default_settings.sh
      sed -i 's/INSTALL_RPC=1/INSTALL_RPC=0/' default_settings.sh

#. Make sure the remaining packages from the table above (**[HyCo] Hybrid Compiler**,
   **[HyCo] ONNX Models for Hybrid Compiler**, and the **SDK1 installer**) have been downloaded
   and prepared as described in **Installation_ReadMe.md** — the installation and the later
   steps depend on them.

#. Run the installation script to set up the Hybrid Compiler and its environment:

   .. code-block:: bash

      # Change to the directory of the extracted installation scripts package first,
      # then run the following command:
      cd installation

      # Run the installation script
      ./install.sh

   It will take some time to complete the installation process.

   .. tip::

      If you encounter network-related issues during the Docker build, such as ``EOF``
      errors while cloning git repositories, set the ``COMPOSE_PARALLEL_LIMIT`` environment
      variable to ``1``. This reduces the number of parallel operations, which eases network
      congestion and makes the build more stable.

      .. code-block:: bash

         export COMPOSE_PARALLEL_LIMIT=1


.. _rpc_server_setup:

Setting Up the RPC Server on the Target Board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

REACTION runs compiled models on the board through a TVM RPC server (Hardware-In-the-Loop).
Its runtime wheels only work with CPython 3.10 (``cp310``), but the R-Car V4H SH board ships
Ubuntu 24.04 with Python 3.12 and has neither ``pip`` nor ``rpm``. The ``python310-*.rpm``
from the Yocto guide therefore does not apply. Install a private CPython 3.10 with ``uv``
instead: no root needed, system Python untouched.

The whole installation is a one-time job driven from the host machine by the
``setup_sh_rpc_server.sh`` script of the
`ros2_demo_workspace <https://github.com/renesas-rdk/ros2_demo_workspace>`_ repository. Download
it on the host machine:

.. code-block:: bash

   # Run this command on the host machine
   wget https://raw.githubusercontent.com/renesas-rdk/ros2_demo_workspace/main/common_utils/setup_sh_rpc_server.sh

If the repository is already cloned, the script is in ``ros2_demo_workspace/common_utils``
instead.

.. important::

   Open the script and adapt the settings at the top to your setup before running it. The
   address, the credentials and the paths below are examples only:

   .. code-block:: bash

      BOARD=ubuntu@192.168.1.100   # <user>@<ip> of the board
      BOARD_PW=ubuntu              # SSH password of the board
      PKG=/path/to/hyco-install    # Root directory of the unpacked HyCo package, i.e. the
                                   # directory that contains both installation/install.sh and
                                   # packages/v4x/*.whl
      XOS_VERSION=v3.43.0          # Installed xOS SDK version, adjust if different

The script needs ``sshpass`` on the host machine, and the board needs working internet access
for this one run: the bootstrap it pushes to the board fetches ``uv`` from
``https://astral.sh/uv/install.sh`` and lets ``uv`` download CPython 3.10 there. The TVM runtime
and Artifact Helper wheels are copied from the host and installed without a package index. All
settings are checked before anything on the board is changed. Run it once:

.. code-block:: bash

   # Run this command on the host machine
   bash setup_sh_rpc_server.sh

Once the script has finished, start the server on the board from that virtual environment
before every evaluation session, using the script that was deployed to ``~/rpc_server``.
``Ctrl+C`` stops the server.

.. code-block:: bash

   # Run this command on the target board
   bash ~/rpc_server/start_rpc_server.sh

.. important::

   Do not set ``rpc_server_auto: true`` in ``reaction.yaml``. The automatic start makes the host
   run ``python3 -m tvm.exec.rpc_server`` over SSH, which resolves to the system Python 3.12
   where TVM is not installed, and fails. The server is not started at boot either, so it must
   be started manually again after a reboot of the board.

See :ref:`REACTION Usage <reaction_usage>` for the ``reaction.yaml`` settings that connect to this server.
