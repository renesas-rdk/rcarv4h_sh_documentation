.. _build_kernel:

Custom Linux Kernel and Device Tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This section describes how to customize and build the Linux kernel and device tree blobs (DTBs) for the R-Car V4H SH by using the `rcar-utils <https://github.com/renesas-rdk/rcar-utils>`_ repository.

Customizing and Building the Linux Kernel
"""""""""""""""""""""""""""""""""""""""""

Use the build script provided in the ``rcar-utils`` repository to build the Linux kernel for the R-Car V4H SH.

Change to the build script directory:

.. code-block:: bash

   cd ~/rcarv4h_workspace/rcar-utils/local-build-scripts

Modify the kernel source as needed by editing the files in the ``linux-sh`` directory.

Build the Linux kernel image and the device tree blobs (DTBs):

.. code-block:: bash

   ./main_build.sh kernel all

The following kernel sub-commands are available:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Sub-command
     - Description
   * - ``all``
     - Configure the kernel, then build the kernel image and every device tree.
   * - ``image``
     - Configure the kernel, then build the kernel image only.
   * - ``dtbs``
     - Configure the kernel, then build the device trees only.
   * - ``modules``
     - Run ``all``, then build the loadable kernel modules.
   * - ``modules-install``
     - Run ``modules``, then install the modules to ``KERNEL_MODULES_OUTPUT_DIR``, together with
       their configuration files and the PCIe PHY firmware. Downloading the firmware needs network
       access the first time; afterwards it is taken from the local download cache.
   * - ``defconfig``
     - Regenerate ``.config`` from the board defconfig and the configuration fragment, discarding
       any local change. Nothing is compiled. See
       :ref:`Customizing and Building the Kernel Configuration <kernel_config>`.
   * - ``menuconfig``
     - Open the kernel configuration editor. The ``.config`` it saves is kept by the builds that
       follow. See
       :ref:`Customizing and Building the Kernel Configuration <kernel_config>`.
   * - ``clean`` / ``distclean``
     - Clean the kernel build outputs.

Every build sub-command configures the kernel before compiling. "Configure" does not always mean
"regenerate": a ``.config`` that has been customized is kept, as described in
:ref:`Customizing and Building the Kernel Configuration <kernel_config>`.

.. note::

   The ``all`` target does **not** build the kernel modules, and none of the ``kernel``
   sub-commands produce a ``fitImage``. Each target is a superset of the previous one, so a
   single command is usually enough:

   * ``./main_build.sh kernel modules-install`` builds the kernel image, the device trees,
     and the modules, and installs the modules.
   * ``./main_build.sh fitimage all`` additionally rebuilds the initramfs, builds the BL31 blob
     when it is missing, and packages everything into ``fitImage``. See
     :ref:`Building the FIT Image <build_fitimage>`.

   The board boots from ``fitImage``, so a change to the kernel or the device tree only takes
   effect once that file has been rebuilt and copied to the board. Deploying a ``.dtb`` or
   ``.dtbo`` on its own has no effect.

.. _kernel_config:

Customizing and Building the Kernel Configuration
"""""""""""""""""""""""""""""""""""""""""""""""""

Customize the kernel configuration to enable a driver or feature that the default configuration
leaves out, such as the driver for a camera sensor you want to attach. See the
`Linux Kernel Configuration Guide <https://www.kernel.org/doc/html/latest/kbuild/kconfig.html>`_
for the mechanics of kconfig itself.

The kernel configuration is not produced by a plain ``make sparrow_hawk_defconfig``. The build
script concatenates two files and lets kconfig fill in the defaults for everything else, which is
what a Yocto kernel build does:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - File
     - Purpose
   * - ``linux-sh/arch/arm64/configs/sparrow_hawk_defconfig``
     - Base configuration for the target platform.
   * - ``linux-sh/arch/arm64/configs/sparrow_hawk.config``
     - Configuration fragment merged on top of the base configuration.

The fragment is applied last, so an option set there overrides the same option in the defconfig.

To change the configuration, add your options to the fragment
``linux-sh/arch/arm64/configs/sparrow_hawk.config``, then rebuild and repackage the FIT image:

.. code-block:: bash

   ./main_build.sh fitimage all

To browse the available options, or to try a setting out without editing the fragment, use the
kernel configuration editor:

.. code-block:: bash

   ./main_build.sh kernel menuconfig

``./main_build.sh kernel defconfig`` is the only sub-command that discards a customized
``.config`` and starts again from the defconfig and the fragment. It builds nothing, which also
makes it a quick way to check that an edited fragment produces the configuration you expect.

.. warning::

   A ``.config`` kept this way is not tracked by git, and ``./main_build.sh kernel distclean``
   removes it along with the stamp file. Copy the options you want to keep into
   ``sparrow_hawk.config``.

.. note::

   ``CONFIG_LOCALVERSION`` and ``CONFIG_LOCALVERSION_AUTO`` are appended by the build script from
   the ``KERNEL_LOCALVERSION`` setting in ``config.ini``, after both files. Whatever the defconfig
   and the fragment set for these two symbols is therefore overridden; change
   ``KERNEL_LOCALVERSION`` instead.

.. tip::

   To check the specific configuration options that are enabled in the default configuration, you can run the following command **on the target board**:

   .. code-block:: bash

      zcat /proc/config.gz | grep "CONFIG_<option_name>"

.. _modify_dts:

Customizing and Building the Device Tree
""""""""""""""""""""""""""""""""""""""""

Use the device tree sources in the ``linux-sh`` repository to modify hardware-related settings such as enabled peripherals, pin control, buses, and attached devices.

For the R-Car V4H SH, the main device tree source file is located at
``linux-sh/arch/arm64/boot/dts/renesas/r8a779g3-sparrow-hawk.dts``.

The device tree overlay source files are located at
``linux-sh/arch/arm64/boot/dts/renesas/r8a779g3-sparrow-hawk-<overlay_name>.dtso``.

Refer to the `Device Tree Usage Guide <https://www.kernel.org/doc/html/latest/devicetree/usage-model.html>`_ for detailed information on how to modify device tree blobs (DTBs) and overlays (DTBOs).

After making changes to the device tree source files, rebuild and repackage the FIT image:

.. code-block:: bash

   ./main_build.sh fitimage all

This single command rebuilds the device tree blobs and packages them into ``fitImage``, so there is
no need to run ``./main_build.sh kernel dtbs`` beforehand. That target only writes the ``.dtb`` and
``.dtbo`` files on the build host, which the board never reads directly.

Adding a New Device Tree Overlay
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A new overlay is not picked up automatically. After creating the ``.dtso`` source file, register it
in two places:

1. Add the ``.dtbo`` target to ``linux-sh/arch/arm64/boot/dts/renesas/Makefile`` so that the kernel
   build produces it.

2. Add the overlay to ``rcar-utils/local-build-scripts/build_fitimage.sh`` so that it is packaged
   into the FIT image, by appending an entry to both arrays:

   .. code-block:: bash

      FIT_OVERLAY_IMAGES=(
          ...
          "fdt-my-overlay|${BOARD_DTB}-my-overlay.dtbo"
      )

      FIT_OVERLAY_CONFIGS=(
          ...
          "my-overlay|fdt-my-overlay|"
      )

   The first array declares the image node that carries the overlay data. The second declares the
   FIT configuration name that selects it at boot time, which is the name appended to the boot
   address as ``#my-overlay``.

If a ``.dtbo`` listed in ``FIT_OVERLAY_IMAGES`` has not been built, the FIT image build stops with
an ``overlay not built`` error.
