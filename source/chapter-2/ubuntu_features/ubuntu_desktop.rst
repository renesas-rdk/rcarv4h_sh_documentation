.. _ubuntu_desktop:

Ubuntu Desktop with R-Car V4H SH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ubuntu Desktop is supported together with the R-Car V4H SH environment.

Main points:

- Ubuntu Desktop environment is available on R-Car V4H SH
- GUI-based operation is supported
- Can be used for development and evaluation
- Suitable for desktop-style workflows on the board

This guide walks you through setting up Ubuntu Desktop on the R-Car V4H SH.

Prerequisites
"""""""""""""

- R-Car V4H SH
- SD card with the Ubuntu image flashed. Please refer to the :ref:`Quick Setup Guide <quick_setup_sh_guide>` for instructions on how to prepare the SD card.
- Monitor and DisplayPort cable
- Internet connection

Detailed Steps
""""""""""""""

The following sections provide detailed steps to set up and use the Ubuntu Desktop environment on the R-Car V4H SH.

Hardware Connection
~~~~~~~~~~~~~~~~~~~

Connect the R-Car V4H SH to a monitor using the DisplayPort interface, and ensure that the board is powered on.

The following figure illustrates the typical desktop setup for the R-Car V4H SH:

.. figure:: ../../images/sh_with_monitor.png
   :alt: R-Car V4H SH Desktop Setup
   :align: center
   :width: 800px

   R-Car V4H SH Desktop Setup

Boot the Board
~~~~~~~~~~~~~~

- Insert the flashed SD card into the R-Car V4H SH board.
- Power on the board.

Initial Boot and Login
~~~~~~~~~~~~~~~~~~~~~~

**Login information:**

- User: ubuntu
- Password: ubuntu

Expand Root Filesystem
~~~~~~~~~~~~~~~~~~~~~~

Expand the root filesystem using the ``parted`` tool to use the full SD card capacity.

If you have already expanded the root filesystem, you can skip this step.

.. code-block:: bash

   # Install parted tool and resize partition
   sudo apt update
   sudo apt install parted

   # Check current disk usage before resize
   df -h

   # Resize the partition to 100% of the disk; replace the partition name if required
   sudo parted /dev/mmcblk0 resizepart 1 100%

   # Resize the filesystem; replace the partition name if required
   sudo resize2fs /dev/mmcblk0p1

Install Ubuntu Desktop
~~~~~~~~~~~~~~~~~~~~~~

Install the minimal Ubuntu desktop environment:

.. code-block:: bash

   sudo apt install ubuntu-desktop-minimal --no-install-recommends -y

For a better user experience, you can also install additional packages:

.. code-block:: bash

   sudo apt install -y \
      fonts-ubuntu \
      fonts-dejavu-extra \
      fonts-liberation \
      fonts-liberation2 \
      fonts-noto-core \
      fonts-noto-extra \
      fonts-noto-cjk \
      fonts-noto-color-emoji \
      fonts-noto-mono \
      fonts-open-sans \
      fonts-roboto \
      fonts-freefont-ttf \
      fonts-droid-fallback

Complete Setup
~~~~~~~~~~~~~~

Reboot the device to start using Ubuntu Desktop:

.. code-block:: bash

   sudo reboot

Notes
~~~~~

- Ensure a stable internet connection during desktop installation.
- The installation process may take some time depending on internet speed.
- After installation and reboot, you should see the Ubuntu Desktop environment instead of Weston.

Troubleshooting
~~~~~~~~~~~~~~~

- If boot fails, verify that SD card boot mode is correctly set.
- For installation issues, check internet connectivity and available disk space.

Switch from ``networkd`` to ``NetworkManager``
""""""""""""""""""""""""""""""""""""""""""""""

The default network manager for the Ubuntu image on R-Car V4H SH is ``networkd``.

If you want to switch to ``NetworkManager`` **to support graphical network management**, follow the steps below:

.. note::

   Use the serial console for the operations below, as switching to NetworkManager may cause the network connection to drop temporarily, which can affect SSH access.

#. On the serial console, enter sudo mode:

   .. code-block:: bash

      sudo -i

#. Stop and disable ``networkd``:

   .. code-block:: bash

      systemctl stop systemd-networkd
      systemctl disable systemd-networkd
      systemctl mask systemd-networkd

#. Install NetworkManager:

   .. code-block:: bash

      apt update
      apt install network-manager

#. Check status:

   .. code-block:: bash

      systemctl status NetworkManager
      nmcli device status

   If NetworkManager is running and the network interfaces are listed, proceed to the next step.

   Otherwise, enable and start NetworkManager:

   .. code-block:: bash

      systemctl unmask NetworkManager
      systemctl enable NetworkManager
      systemctl start NetworkManager

#. Back up the netplan configuration and edit it to use NetworkManager as the renderer:

   .. code-block:: bash

      cp -a /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml.bak

   Edit the netplan file. For example:

   .. code-block:: bash

      vi /etc/netplan/50-cloud-init.yaml

   Change:

   .. code-block:: yaml

      renderer: networkd

   to:

   .. code-block:: yaml

      renderer: NetworkManager

   Example:

   .. code-block:: yaml

      network:
        version: 2
        renderer: NetworkManager
        ethernets:
          end0:
            dhcp4: true

#. Apply netplan:

   .. code-block:: bash

      netplan apply

Limitations
"""""""""""

The graphics stack used by Ubuntu Desktop on the R-Car V4H SH is:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Component
     - Description
   * - GPU
     - PowerVR AXM-8-256 (BVNC 30.3.408.101), 1 compute unit at 599 MHz.
   * - Vendor driver
     - DDK 25.1 binary blob. Provides OpenGL ES 3.2, Vulkan 1.4 and OpenCL 3.0.
       It provides **no desktop OpenGL** and **no Vulkan WSI**.
   * - Desktop OpenGL
     - Provided by Mesa **zink**, layered on top of the PowerVR Vulkan ICD.
   * - Desktop session
     - Ubuntu 24.04 with GNOME 46 on Wayland.

Because the vendor driver is a binary blob with several gaps, the desktop session ships with a
set of workarounds. They are applied automatically by the session environment, so applications
must be started from inside the desktop session in order to inherit them.

.. warning::

   The set of workarounds may not be complete. Some applications may not work correctly, or may crash, due to missing features in the vendor driver.

   Please report any issues to the `GitHub repository's issues <https://github.com/renesas-rdk/rcarv4h_sh_documentation/issues>` for further support.

What Runs on the GPU and on the CPU
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With the workarounds above in place, the following work is accelerated by the GPU:

- The compositor, through the vendor EGL library.
- Xwayland and glamor.
- All X11/GLX and OpenGL ES clients through zink, for example rviz2, Gazebo and glxgears.
- WebGL in Chromium and Electron applications, through ANGLE.
- OpenCL 3.0 compute.

The following work runs on the CPU:

- GTK4 applications, which render with cairo.
- WebKitGTK page content.
- Electron user interface compositing.
- cheese.
- Camera JPEG decode.
