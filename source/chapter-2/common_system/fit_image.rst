.. _build_fitimage:

Building the FIT Image
^^^^^^^^^^^^^^^^^^^^^^

The ``fitimage`` target assembles the ``fitImage`` that U-Boot loads. It bundles the following into
a single file:

* the kernel image,
* the base DTB,
* every device tree overlay, each exposed as its own FIT configuration,
* the ARM Trusted Firmware BL31 blob,
* the U-Boot boot script,
* the initramfs.

Every one of them is built from source, so a single command produces a complete boot image:

.. code-block:: bash

   ./main_build.sh fitimage all

The following ``fitimage`` sub-commands are available:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Sub-command
     - Description
   * - ``all``
     - Build the kernel image, the device trees and the kernel modules, then the BL31 blob and
       the initramfs, and assemble the FIT image.
   * - ``image``
     - Assemble the FIT image from an existing kernel build, without rebuilding the kernel. The
       BL31 blob and the initramfs are built only when they are missing.
   * - ``clean``
     - Remove ``FIT_OUTPUT_DIR``.

The build writes the following files to ``FIT_OUTPUT_DIR``:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - File
     - Description
   * - ``fitImage``
     - The FIT image to deploy to the target board.
   * - ``fit-image.its``
     - Generated image tree source describing the contents of the FIT image. Set ``FIT_ITS`` in
       ``config.ini`` to use a hand-written one instead.
   * - ``Image``, ``*.dtb``, ``*.dtbo``,
       ``bl31-sparrow-hawk.bin``,
       ``uInitramfs.cpio.gz``, ``boot.cmd``
     - Staged copies of the inputs referenced by ``fit-image.its``.

.. note::

   The BL31 blob is mandatory: the bootable configurations load it, and the build stops if it is
   missing. It is built from source by the ``bl31`` target, which ``fitimage`` runs itself when
   the blob is not there, so no additional setup is required. See
   :ref:`Building the ARM Trusted Firmware BL31 Blob <build_bl31>`.

.. important::

   ``fitimage all`` rebuilds the initramfs together with the kernel. The initramfs carries
   ``pcie-rcar-gen4.ko``, whose vermagic has to match the kernel packaged in the same
   ``fitImage``; a stale module would only fail at ``switch_root`` time, long after the boot
   looks successful. ``fitimage image`` reuses an existing initramfs instead, so use it only when
   the kernel has not changed.

FIT Configurations
""""""""""""""""""

``fitImage`` contains two kinds of configuration. ``default`` and ``initramfs`` are the bootable
ones: they carry the kernel, the base DTB and the BL31 blob. Every other configuration carries
nothing but one device tree overlay, so it is not bootable on its own and has to be combined with
one of the two.

A configuration is selected by appending its name to the boot address with a ``#`` separator, and
several can be combined:

.. code-block:: bash

   bootm ${loadaddr}#default#uio

The generated FIT image provides the following configurations:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Configuration
     - Description
   * - ``default``
     - Kernel, base DTB and BL31 blob. This is the default configuration.
   * - ``initramfs``
     - Same as ``default``, plus the initramfs. Only present when an initramfs was packaged.
   * - ``uio``
     - Exposes the R-Car V4H hardware IP through UIO. Required by the CNN-IP, among others.
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
     - Raspberry Pi Touch Display 2, 5-inch / 7-inch model. ``rpi-display-2`` is kept as an alias
       of the 7-inch model for backward compatibility.
   * - ``ws-display-13in``
     - Waveshare 13.3-inch MIPI DSI panel. ``waveshare-panel`` is kept as an alias for backward
       compatibility.
   * - ``olimex-dsi-hdmi``
     - Olimex DSI-to-HDMI adapter.

.. tip::

   The FIT image also embeds ``boot.cmd`` as a U-Boot script, which builds the configuration
   string automatically. It always adds ``#uio``, probes the I2C buses to detect which camera is
   on J1 and J2 and which display is on J4, reads the ``fan`` environment variable to add the
   matching fan overlay, and selects ``#initramfs`` instead of ``#default`` when ``root=`` in
   ``bootargs`` is not an ``mmcblk`` device.

   To add a configuration it does not select on its own, set the ``conf_append`` environment
   variable in U-Boot: its value is appended to the end of the configuration string it builds.

.. _build_bl31:

Building the ARM Trusted Firmware BL31 Blob
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The bootable FIT configurations load the BL31 blob through ``loadables``, and the FIT image build
stops when the blob is missing. The ``bl31`` target builds it from the ARM Trusted Firmware
source:

.. code-block:: bash

   ./main_build.sh bl31 all

The source is cloned from ``TFA_URL`` at the revision pinned in ``TFA_SRCREV`` into
``TFA_SRC_DIR``, and built for ``PLAT=rcar_gen4`` with ``LSI=V4H``. The following ``bl31``
sub-commands are available:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Sub-command
     - Description
   * - ``all`` / ``image``
     - Fetch the source if needed, then build the blob.
   * - ``fetch``
     - Re-clone the source at the pinned revision.
   * - ``clean``
     - Clean the TF-A build tree and remove ``TFA_OUTPUT_DIR``.

The build writes three files to ``TFA_OUTPUT_DIR``, which defaults to
``rcar-utils/workspace/arm-trusted-firmware/release/``:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - File
     - Description
   * - ``bl31-sparrow-hawk.bin``
     - The blob packaged into ``fitImage``.
   * - ``bl31-sparrow-hawk.elf``,
       ``bl31-sparrow-hawk.srec``
     - Same firmware in ELF and S-record form, for debugging and for flashing.

.. note::

   The ``fitimage`` target builds BL31 itself when the blob is missing, and reuses it otherwise:
   BL31 does not depend on the kernel, so it does not have to be rebuilt with it. Run
   ``./main_build.sh bl31 all`` to rebuild it explicitly, for example after changing
   ``TFA_SRCREV``.

   Setting ``BL31_BIN`` in ``config.ini`` points the FIT image at a blob from another build. That
   blob is then used as it is and never rebuilt, and the build stops if the path does not exist.

.. _build_initramfs:

Building the Initramfs
^^^^^^^^^^^^^^^^^^^^^^

The initramfs is only needed to boot a root filesystem that is **not** on the microSD card or on
eMMC, such as an NVMe SSD behind PCIe. The PCIe controller driver is built as a module, so on such
a setup the driver needed to reach the root filesystem lives inside the root filesystem itself.
The initramfs breaks that loop: it loads the driver, waits for the root device to appear, and then
hands over to the real init with ``switch_root``.

Build it with:

.. code-block:: bash

   ./main_build.sh initramfs all

The following ``initramfs`` sub-commands are available:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Sub-command
     - Description
   * - ``all`` / ``image``
     - Build busybox if needed, stage the tree, and pack ``uInitramfs.cpio.gz``.
   * - ``busybox``
     - Build the statically linked busybox only.
   * - ``clean``
     - Remove the busybox tree, the staged root filesystem and ``uInitramfs.cpio.gz``.

The image is written to ``INITRAMFS_OUTPUT_DIR``, which defaults to
``rcar-utils/workspace/initramfs/``, and contains only what is needed to reach the root
filesystem: a statically linked busybox, ``pcie-rcar-gen4.ko`` taken from the kernel build, the
PCIe PHY firmware that the driver requests while bringing the link up, and the ``init`` script.

.. important::

   This target needs the kernel modules of the current kernel build, so run
   ``./main_build.sh kernel modules`` first if you have not built them yet. Otherwise the build
   stops with an error naming the missing ``pcie-rcar-gen4.ko``.

   ``./main_build.sh fitimage all`` takes care of the ordering itself: it builds the kernel and
   its modules, then the initramfs, and then packages both.

.. note::

   If the board drops to an ``initramfs:`` shell during boot, the init script could not reach the
   root filesystem. It prints the reason and lists the block devices it can see, which
   distinguishes a driver that failed to load from a root device that never appeared.

.. _build_ext_modules:

Building the Out-of-Tree Kernel Modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some drivers are not part of the kernel source tree and are built separately by the
``ext-modules`` target:

.. list-table::
   :header-rows: 1
   :widths: 20 45 35

   * - Module
     - Description
     - Installed to
   * - ``cmemdrv``
     - Contiguous memory allocator used by the multimedia and CNN stacks.
     - ``usr/lib/modules/<release>/updates/``
   * - ``qos``
     - Quality-of-service settings for the memory controller.
     - ``usr/lib/modules/<release>/extra/``
   * - ``pvrsrvkm``
     - PowerVR GPU kernel module.
     - ``usr/lib/modules/<release>/extra/``

The sources are fetched automatically at the revisions pinned in ``config.ini`` and patched with
the patches under ``local-build-scripts/patches/``, so only a built kernel is required.

Build and install them to ``KERNEL_MODULES_OUTPUT_DIR``:

.. code-block:: bash

   ./main_build.sh ext-modules install

The following ``ext-modules`` sub-commands are available:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Sub-command
     - Description
   * - ``all``
     - Fetch the sources if needed, then build the modules.
   * - ``fetch``
     - Re-clone the sources at the pinned revisions and re-apply the patches.
   * - ``install``
     - Build the modules and install them to ``KERNEL_MODULES_OUTPUT_DIR``.
   * - ``clean``
     - Clean the module build outputs.

Besides the modules themselves, ``install`` writes the files the modules need in order to be
usable on the board:

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - File in ``KERNEL_MODULES_OUTPUT_DIR``
     - Purpose
   * - ``usr/lib/modules-load.d/cmemdrv.conf``,
       ``usr/lib/modprobe.d/cmemdrv.conf``
     - Load ``cmemdrv`` at boot and reserve ``CMEM_BSIZE`` bytes for it.
   * - ``usr/lib/firmware/rgx.fw.*``,
       ``usr/lib/firmware/rgx.sh.*``
     - PowerVR GPU firmware from the same release as the module.

       Without it ``pvrsrvkm`` fails with a version mismatch.
   * - ``usr/include/linux/cmemdrv.h``,
       ``usr/include/qos_public_common.h``
     - Headers for applications built against these drivers.

.. important::

   These modules must be rebuilt whenever the kernel is rebuilt. They are compiled against the
   kernel in ``KERNEL_DIR`` and are installed under the kernel release string, so a kernel built
   with a different configuration or ``KERNEL_LOCALVERSION`` leaves them in a directory the running
   kernel does not load.