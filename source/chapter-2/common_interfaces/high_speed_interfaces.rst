High-Speed Interfaces
^^^^^^^^^^^^^^^^^^^^^

The R-Car V4H SH is equipped with several high-speed interfaces that enable users to connect a variety of peripherals and expansion modules.

This section describes the high-speed interface unit of the R-Car V4H SH.

PCIe 4.0
""""""""

The PCIe 4.0 interface on the R-Car V4H SH allows for high-speed data transfer and connectivity with compatible PCIe devices.

For example, you can connect a PCIe NVMe SSD to enhance storage performance. The following steps describe how to set up and use a PCIe NVMe SSD with the R-Car V4H SH.

- Hardware requirements:

  - M.2 NVMe SSD.

- Hardware setup:

  #. Power off the R-Car V4H SH.
  #. Insert the M.2 NVMe SSD into the **CN5 M.2 Key-M slot** on the R-Car V4H SH.
  #. Power on the R-Car V4H SH.

.. caution::

   Handle the M.2 NVMe SSD with care to avoid damage from static electricity.

Usage example with pciutils:

First, install the ``pciutils`` package if it is not already installed:

.. code-block:: bash

   sudo apt install pciutils

To list all PCIe devices connected to the system, use the following command:

.. code-block:: bash

   lspci

Example output:

.. code-block:: console
   :emphasize-lines: 2

   0000:00:00.0 PCI bridge: Renesas Technology Corp. Device 0030
   0000:01:00.0 Non-Volatile memory controller: Realtek Semiconductor Co., Ltd. RTS5765DL NVMe SSD Controller (DRAM-less) (rev 01)
   0001:00:00.0 PCI bridge: Renesas Technology Corp. Device 0030
   0001:01:00.0 USB controller: Renesas Technology Corp. uPD720201 USB 3.0 Host Controller (rev 03)

To check whether the NVMe SSD is recognized by the system, use the following command:

.. code-block:: bash

   lsblk

Example output (this SSD is recognized as ``nvme0n1`` and has a single partition ``nvme0n1p1``):

.. code-block:: console
   :emphasize-lines: 8,9

   NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
   mtdblock0    31:0    0 116.5K  1 disk
   mtdblock1    31:1    0   1.8M  1 disk
   mtdblock2    31:2    0   128K  1 disk
   mtdblock3    31:3    0    14M  0 disk
   mmcblk0     179:0    0  29.7G  0 disk
   └─mmcblk0p1 179:1    0  29.7G  0 part /
   nvme0n1     259:0    0 238.5G  0 disk
   └─nvme0n1p1 259:1    0   6.2G  0 part

Mount the NVMe SSD:

.. code-block:: bash

   sudo mkdir /mnt/nvme
   sudo mount /dev/nvme0n1p1 /mnt/nvme

Unmount the NVMe SSD:

.. code-block:: bash

   sudo umount /mnt/nvme
   sudo rmdir /mnt/nvme

If you want to boot from the NVMe SSD, refer to the :ref:`Boot from NVMe SSD <boot_from_nvme>` section for detailed instructions.

MIPI-CSI camera x2
""""""""""""""""""

The R-Car V4H SH features dual MIPI-CSI connectors that support camera input for applications requiring image capture and processing.

.. note::

   #. The **Raspberry Pi Camera V2** (IMX219), the **Raspberry Pi Camera V3** (IMX708) and
      **IMX462**-based modules are supported. The bootloader probes J1 and J2 and applies the
      matching camera overlay automatically; see
      :ref:`Device Tree Overlay <device_tree_overlay>`.
   #. The Raspberry Pi Camera V3 is currently under development on mainline Linux and libcamera, so at this stage the image may appear dark and features such as auto-focus are not yet supported.
      In addition, recognition may occasionally fail.
   #. The board connector has 22 pins, so a 15-pin-to-22-pin conversion cable is required.
   #. When using the Raspberry Pi Camera V2, a `Raspberry Pi camera cable
      <https://www.raspberrypi.com/products/camera-cable/>`_ is required.

Set up the MIPI-CSI interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect Raspberry Pi Camera V2 and/or Raspberry Pi Camera V3 to J1 and/or J2 connector.

.. figure:: ../../images/camera_connect.png
   :alt: Raspberry Pi Camera V2 connected to J1 and J2
   :align: center
   :width: 800px

   Raspberry Pi Camera V2 connected to J1 and J2

.. note::

   The following example commands and output are for the Raspberry Pi Camera V3.
   The Raspberry Pi Camera V2 is also supported, but the output may differ slightly.

The J1/J2 cameras are driven by libcamera, not by a plain ``/dev/video`` node.
The ``libcamera-v4h`` package provides the ``cam`` utility, the ``libcamerify``
shim, the ``libcamerasrc`` GStreamer element and the Python 3 bindings.

The GStreamer example below also requires the following packages:

.. code-block:: bash

   sudo apt update
   sudo apt install gstreamer1.0-tools gstreamer1.0-plugins-good

To confirm that the camera is detected, use the following command:

.. code-block:: bash

   cam -l

Example output:

.. code-block:: console
   :emphasize-lines: 1

   1: External camera 'imx708' (/base/soc/i2c@e6508000/sensor@1a)

.. seealso::

   Example usage of the camera with ROS 2:

   #. Install the ``ros-jazzy-gscam`` package:

      .. code-block:: bash

         sudo apt install ros-jazzy-gscam

   #. Run the ``gscam_node`` with the appropriate parameters:

      .. code-block:: bash

         source /opt/ros/jazzy/setup.bash
         ros2 run gscam gscam_node --ros-args \
         -p gscam_config:="libcamerasrc ! video/x-raw,width=1536,height=864 ! videoconvert" \
         -p camera_name:=v4h -p frame_id:=camera

Legacy V4L2 applications run through the ``libcamerify`` shim. The libcamera
node is ``/dev/video2``:

.. code-block:: bash

   libcamerify v4l2-ctl -d /dev/video2 --all

The following commands list the remaining capabilities of the camera:

- ``cam -c1 -I`` lists the supported formats. Only XRGB8888 and NV16 at
  1536x864 or 2304x1296 are available. There is no scaler, so any other
  resolution must be scaled downstream.
- ``cam -c1 --list-controls`` lists the exposure, gain, AWB and gamma controls.
- ``gst-inspect-1.0 libcamerasrc`` lists the same controls as GStreamer
  properties.

.. _high_speed_interfaces_set_static_ip:

Ethernet AVB - 1 Gbps
"""""""""""""""""""""

The Gigabit Ethernet port on the R-Car V4H SH provides high-speed network connectivity for data communication and internet access.

Connect the network cable to the Gigabit Ethernet port before using the Ethernet interface.

The current Ubuntu netplan configures the system to obtain its network settings via DHCP.

After connecting the Ethernet cable, use the following command to confirm the network configuration.

To list all network interfaces and their IP addresses:

.. code-block:: bash

   ip a

To test network connectivity to an external server, use the ``ping`` command:

.. code-block:: bash

   ping -c 4 bing.com
   ping -c 4 8.8.8.8

Set a Static IP Address
~~~~~~~~~~~~~~~~~~~~~~~

In Ubuntu, the network is configured with Netplan. If you need to set a static IP address for the Ethernet interface, for example ``169.254.43.99``, follow these steps:

- Open the network configuration file with ``vi``:

  .. code-block:: bash

     sudo vi /etc/netplan/50-cloud-init.yaml

- Modify the file to set a static IP address. For example:

  .. code-block:: yaml

     # This file describes the network interfaces available on your system
     # For more information, see netplan(5).
     network:
       version: 2
       renderer: networkd
       ethernets:
         end0:
           dhcp4: false
           addresses: [169.254.43.99/24]
           routes:
             - to: default
               via: 169.254.43.86
           nameservers:
             addresses: [8.8.8.8, 8.8.4.4]

  .. note::

     Make sure to replace the ``addresses`` and ``routes`` values with the appropriate values for your network.

     If your system uses a different Netplan configuration file under ``/etc/netplan/``, modify that file instead.

- Apply the changes with the following command:

  .. code-block:: bash

     sudo netplan apply

Set DHCP
~~~~~~~~

If you want to revert to DHCP configuration, modify the ``/etc/netplan/50-cloud-init.yaml`` file as follows:

.. code-block:: yaml

   # This file describes the network interfaces available on your system
   # For more information, see netplan(5).
   network:
     version: 2
     renderer: networkd
     ethernets:
       end0:
         dhcp4: yes

Apply the changes with the following command:

.. code-block:: bash

   sudo netplan apply

Set a MAC Address
~~~~~~~~~~~~~~~~~

When you connect two or more R-Car V4H SH boards to the same network (using the same router), you may encounter an issue where you cannot reach the boards over the network.

This is due to duplicate MAC addresses. Because the R-Car V4H SH uses a random MAC address by default, multiple boards might acquire the same MAC address.

Consequently, two devices with the same MAC address will cause conflicts on the router, preventing network access.

The easiest way to resolve this is to assign a static MAC address to each device. Edit the ``/etc/netplan/50-cloud-init.yaml`` file as follows:

.. code-block:: bash

   sudo vi /etc/netplan/50-cloud-init.yaml

Add or modify the configuration to include your custom MAC address:

.. code-block:: yaml

   # This file describes the network interfaces available on your system
   # For more information, see netplan(5).
   network:
     version: 2
     renderer: networkd
     ethernets:
       end0:
         dhcp4: yes
         macaddress: "02:00:00:11:22:34"

Then apply the changes:

.. code-block:: bash

   sudo netplan apply

USB 3.0 Type A x2 and USB Type-C x2
"""""""""""""""""""""""""""""""""""

The R-Car V4H SH includes two USB 3.0 Type-A ports and two USB 3.0 Type-C ports that support high-speed data transfer for connecting various USB peripherals, such as external storage devices, cameras, and input devices.

To use these devices, simply connect them to the USB 3.0 Type-A or Type-C ports.

Verify USB 3.0 Functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To verify that the USB 3.0 ports are functioning correctly, you can use the following command to list USB devices and check their connection speed:

.. code-block:: bash

   lsusb -t

Example output:

.. code-block:: console

   /:  Bus 001.Port 001: Dev 001, Class=root_hub, Driver=xhci-pci-renesas/4p, 480M
      |__ Port 002: Dev 003, If 0, Class=Hub, Driver=hub/4p, 480M
         |__ Port 001: Dev 005, If 0, Class=Video, Driver=uvcvideo, 480M
         |__ Port 001: Dev 005, If 1, Class=Video, Driver=uvcvideo, 480M
         |__ Port 001: Dev 005, If 2, Class=Audio, Driver=snd-usb-audio, 480M
         |__ Port 001: Dev 005, If 3, Class=Audio, Driver=snd-usb-audio, 480M
      |__ Port 003: Dev 004, If 0, Class=Human Interface Device, Driver=usbhid, 1.5M
      |__ Port 003: Dev 004, If 1, Class=Human Interface Device, Driver=usbhid, 1.5M
      |__ Port 004: Dev 002, If 0, Class=Human Interface Device, Driver=usbhid, 1.5M
   /:  Bus 002.Port 001: Dev 001, Class=root_hub, Driver=xhci-pci-renesas/4p, 5000M
      |__ Port 002: Dev 002, If 0, Class=Hub, Driver=hub/4p, 5000M

USB Wi-Fi Adapter Support
~~~~~~~~~~~~~~~~~~~~~~~~~

The following USB Wi-Fi adapters have been tested and are compatible with the R-Car V4H SH:

- Ralink Technology, Corp. MT7601U Wireless Adapter
- AC1300 TP-Link T3U Nano
- TL-WDN6200

.. note::

   If you want to use a different USB Wi-Fi adapter, make sure the required driver is available for the R-Car V4H SH.

   You need to identify the appropriate driver for the USB Wi-Fi adapter and enable it in the Linux kernel configuration file. For example, add ``CONFIG_MT7601U=y`` to ``linux-sh/arch/arm64/configs/sparrow_hawk.config``, then rebuild and deploy the kernel image.

   Refer to the :ref:`Custom Linux Kernel and Device Tree <build_kernel>` section for instructions on how to add support for additional drivers by modifying the Linux kernel.

Usage Example
~~~~~~~~~~~~~

- Install necessary packages

  .. code-block:: bash

     sudo apt update
     sudo apt install rfkill iw wpasupplicant

- Check USB devices

  First, connect the USB Wi-Fi adapter to the R-Car V4H SH.

  Then, run the following command to list all connected USB devices:

  .. code-block:: bash

     lsusb

  Example output:

  .. code-block:: console
     :emphasize-lines: 4,6

     Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
     Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
     Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
     Bus 003 Device 003: ID 2357:0138 TP-Link 802.11ac NIC
     Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
     Bus 005 Device 003: ID 148f:7601 Ralink Technology, Corp. MT7601U Wireless Adapter

- Check interface name

  .. code-block:: bash

     ip a | grep wl

  Example output:

  .. code-block:: console

     7: wlx98ba5f1918cf: <BROADCAST,MULTICAST,DYNAMIC> mtu 1500 qdisc noqueue state DOWN group default qlen 1000

- Unlock the Wi-Fi interface (if necessary)

  .. code-block:: bash

     sudo rfkill list wifi                # Check if the Wi-Fi interface is blocked
     sudo rfkill unblock wifi             # If it is blocked, unblock the Wi-Fi interface
     sudo rfkill list wifi                # Verify that the Wi-Fi interface is now unblocked

  Example output:

  .. code-block:: console

     0: phy0: Wireless LAN
        Soft blocked: no
        Hard blocked: no

- Bring up the Wi-Fi interface

  .. code-block:: bash

     sudo ip link set wlx98ba5f1918cf up  # Bring up the Wi-Fi interface
     ip a | grep wl                       # Check the interface status again

  Example output:

  .. code-block:: console

     7: wlx98ba5f1918cf: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default qlen 1000

- Scan for available Wi-Fi networks

  .. code-block:: bash

     sudo iw dev wlx98ba5f1918cf scan | grep "<YOUR_SSID>"

- Modify network configuration to connect to the Wi-Fi network by editing the Netplan configuration file:

  .. code-block:: bash

     sudo vi /etc/netplan/50-cloud-init.yaml

  Add the following configuration to connect to the Wi-Fi network (replace ``MY_SSID`` and ``MY_PASSWORD`` with your actual Wi-Fi SSID and password):

  .. code-block:: yaml

     network:
       version: 2
       renderer: networkd
       ethernets:
         end0:
           dhcp4: true
       wifis:
         wlx98ba5f1918cf:
           dhcp4: true
           access-points:
             "MY_SSID":
               password: "MY_PASSWORD"

- Apply the changes with the following command:

  .. code-block:: bash

     sudo netplan apply

- Test network connectivity

  .. code-block:: bash

     ping -I wlx98ba5f1918cf bing.com

  Example output:

  .. code-block:: console

     PING bing.com (150.171.27.10) from 192.168.19.177 wlx98ba5f1918cf: 56(84) bytes of data.
     64 bytes from 150.171.27.10: icmp_seq=1 ttl=120 time=420 ms
     64 bytes from 150.171.27.10: icmp_seq=2 ttl=120 time=482 ms
     --- bing.com ping statistics ---
     2 packets transmitted, 2 received, 0% packet loss, time 1001ms
     rtt min/avg/max/mdev = 419.837/451.166/482.495/31.329 ms
