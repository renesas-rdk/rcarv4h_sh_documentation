.. _device_tree_overlay:

Device Tree Overlay
^^^^^^^^^^^^^^^^^^^

A device tree overlay (DTO) is a fragment of device tree that is merged into the base device tree
before the kernel starts. It can add, remove, or modify nodes and properties, which makes it
possible to describe an optional piece of hardware — a camera module, a display panel, a fan —
without maintaining a separate device tree for every possible combination.

On the R-Car V4H SH, overlays are shipped inside ``/boot/fitImage`` and are selected by U-Boot at
boot time. In the normal case the selection is automatic: the board detects what is connected and
applies the matching overlays, so you do not have to configure anything.

How Overlays Are Delivered
""""""""""""""""""""""""""

Every overlay is packaged into ``fitImage`` as its own FIT *configuration*. A configuration is
selected by appending its name to the boot address with a ``#`` separator, and several can be
combined:

.. code-block:: bash

   bootm <addr>#<base-config>#<overlay-config>#<overlay-config>...

- The **first** configuration is the base one. It supplies the kernel, the base device tree, the
  BL31 blob and, when present, the initramfs.
- Every **following** configuration contributes only its device tree fragment, which U-Boot
  applies as an overlay, **in the order written**.

.. note::

   Overlays are never applied with ``fdt apply`` from the U-Boot shell on this board. The only
   supported way to apply one is to name its configuration in the ``bootm`` command line, as shown
   above.

Boot Flow
"""""""""

The configuration string is assembled at boot time by ``boot.cmd``, a U-Boot script that is itself
packaged inside ``fitImage``:

.. code-block:: text

   bootcmd                                          (U-Boot environment, stored in SPI flash)
     └─ run autoconf_mmc | autoconf_nvme | autoconf_usb
          ├─ setenv bootargs "rw root=<device> rootwait"
          ├─ load <interface> 0:1 ${loadaddr} /boot/fitImage
          └─ source ${loadaddr}:script              → executes boot.cmd from inside fitImage
               ├─ probes the I2C buses to detect cameras and the display, and reads the fan variable
               ├─ derives the base configuration from root= in bootargs
               └─ bootm ${loadaddr}${conf}

``source ${loadaddr}:script`` means "execute the ``script`` sub-image of the FIT image loaded at
``${loadaddr}``". This is the mechanism that lets the boot image itself decide which overlays are
applied. On a normal boot you type nothing.

Just before booting, ``boot.cmd`` echoes the command it is about to run, for example:

.. code-block:: text

   bootcmd: bootm 0x58000000#initramfs#uio#fan-argon40

.. tip::

   That line is the single best place to start when a peripheral does not come up. It shows
   exactly which overlays were selected on this boot.

Available Configurations
""""""""""""""""""""""""

``fitImage`` contains two kinds of configuration. ``default`` and ``initramfs`` are the bootable
ones. Every other configuration carries nothing but one overlay, so it is not bootable on its own
and always has to follow one of the two.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Configuration
     - Description
   * - ``default``
     - Kernel, base device tree and BL31 blob. Used when the root filesystem is on the microSD
       card or on eMMC.
   * - ``initramfs``
     - Same as ``default``, plus the initramfs. Used when the root filesystem is on any other
       device, such as an NVMe SSD or a USB storage device.
   * - ``uio``
     - Exposes the R-Car V4H hardware IP (IMP, IMR, IMS and CMEM) through UIO. Required by
       the CNN-IP, among others.
   * - ``j1-imx219`` / ``j2-imx219``
     - IMX219 camera on connector J1 / J2.
   * - ``j1-imx462`` / ``j2-imx462``
     - IMX462 camera on connector J1 / J2.
   * - ``j1-imx708`` / ``j2-imx708``
     - IMX708 camera on connector J1 / J2.
   * - ``fan-pwm``
     - PWM-controlled fan.
   * - ``fan-argon40``
     - Argon40 fan.
   * - ``rpi-display-2-5in`` / ``rpi-display-2-7in``
     - Raspberry Pi Touch Display 2, 5-inch / 7-inch model.
   * - ``ws-display-13in``
     - Waveshare 13.3-inch MIPI DSI panel.
   * - ``olimex-dsi-hdmi``
     - Olimex MIPI-DSI to HDMI adapter (LT8912B).
   * - ``rpi-display-2`` / ``waveshare-panel``
     - Aliases of ``rpi-display-2-7in`` and ``ws-display-13in``, kept for backward compatibility.
       Use the explicit names in new work.

Automatic Detection
"""""""""""""""""""

``boot.cmd`` probes the I2C buses and the boot arguments, and builds the configuration string from
the result:

.. list-table::
   :header-rows: 1
   :widths: 20 45 35

   * - Slot
     - Detection
     - Configuration added
   * - Base
     - ``root=`` in ``bootargs`` points to an ``mmcblk`` device
     - ``#default``
   * - Base
     - ``root=`` points to anything else, such as ``/dev/nvme0n1p1`` or ``/dev/sda1``
     - ``#initramfs``
   * - UIO
     - Always applied
     - ``#uio``
   * - Camera J1
     - Device answers at I2C address ``0x10`` on bus 1
     - ``#j1-imx219``
   * - Camera J1
     - Device answers at ``0x1a`` and its chip ID reads ``0x0708``
     - ``#j1-imx708``
   * - Camera J1
     - Device answers at ``0x1a`` with any other chip ID
     - ``#j1-imx462``
   * - Camera J2
     - Same three rules, on bus 2
     - ``#j2-imx219`` / ``#j2-imx708`` / ``#j2-imx462``
   * - Display J4
     - On bus 0, after the mux at ``0x71`` is switched to channel ``0x07`` and the bus is
       slowed to 100 kHz: the panel controller at ``0x45`` answers and is power-cycled, then
       the touch controller at ``0x5d`` reports config version ``0x41``
     - ``#rpi-display-2-7in``
   * - Display J4
     - Same, config version ``0x42``
     - ``#rpi-display-2-5in``
   * - Display J4
     - ``0x45`` answers and a device also answers at ``0x41``. This check runs after the
       ``0x5d`` check, so it wins when both match
     - ``#ws-display-13in``
   * - Display J4
     - Nothing answers at ``0x45``, but the LT8912B answers at ``0x48``
     - ``#olimex-dsi-hdmi``
   * - Display J4
     - Nothing answers at ``0x45`` or ``0x48``, or ``0x45`` answers but neither a config
       version of ``0x41``/``0x42`` nor a device at ``0x41`` is found
     - None. No display overlay is applied.
   * - Fan
     - The ``fan`` U-Boot environment variable is set to ``argon40`` **and** a device answers at
       ``0x1a`` on bus 3
     - ``#fan-argon40``
   * - Fan
     - The ``fan`` variable is set to ``pwm``. No hardware is probed.
     - ``#fan-pwm``

.. note::

   Fan selection is driven by the ``fan`` U-Boot environment variable, which ``boot.cmd`` never
   sets itself. Set it once from the U-Boot prompt so the selection is explicit:

   .. code-block:: bash

      setenv fan pwm      # or: setenv fan argon40
      saveenv

   The ``bootcmd:`` line echoed just before booting shows which fan overlay was actually
   selected.

The configurations are always assembled in this fixed order:

.. code-block:: text

   base -> uio -> J1 camera -> J2 camera -> J4 display -> fan -> conf_append

Because overlays are applied from left to right, a later one can override properties set by an
earlier one, and anything you add through ``conf_append`` is applied last.

To create a new overlay or change which overlays are packaged into ``fitImage``, refer to
:ref:`Building the FIT Image <build_fitimage>`.
