Overview
^^^^^^^^

The R-Car/V4H SH uses Linux kernel |kernel_version| from the **R-Car Community team**, whose
sources live in `linux-sh <https://github.com/renesas-rdk/linux-sh>`_. Every component is rebuilt
on an **Ubuntu 24.04** host.

Every input the board boots is built from source by the ``rcar-utils`` build scripts, which provide
one target per component:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Target
     - Builds
   * - ``kernel``
     - Kernel image, device trees and loadable kernel modules.
   * - ``ext-modules``
     - Out-of-tree kernel modules: ``cmemdrv``, ``qos`` and the PowerVR GPU module.
   * - ``bl31``
     - ARM Trusted Firmware BL31 blob, loaded by the bootable FIT configurations.
   * - ``initramfs``
     - ``uInitramfs.cpio.gz``, needed to boot a root filesystem that is not on microSD or eMMC.
   * - ``fitimage``
     - ``fitImage``, the single file U-Boot loads. It bundles the kernel image, the device trees,
       the BL31 blob and the initramfs. Kernel modules are not part of it and are deployed to the
       root filesystem separately.

Prerequisites
^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - **Item**
     - **Description / Link**
   * - Build host
     - Ubuntu 24.04, either a physical machine or a Docker container based on an Ubuntu 24.04
       image. The latter also covers Windows and macOS hosts.
   * - `linux-sh <https://github.com/renesas-rdk/linux-sh>`_
     - Linux kernel source code for the R-Car/V4H SH.
   * - `rcar-utils <https://github.com/renesas-rdk/rcar-utils>`_
     - Build scripts used throughout this section.
   * - Internet access
     - Required to clone the sources and download the build dependencies.
   * - SSH and rsync access
     - Between build host and target board, with ``rsync`` installed on both, to copy the build
       artifacts.

Available AI Agent Skills
^^^^^^^^^^^^^^^^^^^^^^^^^

Skills for the R-Car/V4H SH kernel build, located in
``rcar-utils/.claude/skills/<name>/SKILL.md``.

.. list-table::
   :header-rows: 1
   :widths: 26 42 32

   * - Skill
     - Purpose
     - Use when
   * - ``rcar-quick-start``
     - Entry point; orients you in the repo and dispatches to the right skill
     - New to the repo, or unsure which skill applies
   * - ``rcar-setup-workspace``
     - Install host packages, clone ``linux-sh``, run toolchain preflight
     - Fresh host/container, or a build fails on a missing tool
   * - ``rcar-build``
     - Build kernel, dtbs, modules, external modules, TF-A BL31, initramfs,
       fitImage (incl. PREEMPT_RT)
     - Building or rebuilding after a source change
   * - ``rcar-customize-kernel-config``
     - Edit ``sparrow_hawk_defconfig`` / config fragment, menuconfig,
       KERNEL_VARIANT
     - Enabling or disabling a driver or kernel feature
   * - ``rcar-customize-devicetree``
     - Edit or add the base ``.dts`` and ``.dtso`` overlays (camera, display,
       fan, UIO)
     - Changing the board hardware description
   * - ``rcar-customize-boot``
     - Edit ``boot.cmd``, U-Boot auto-detection, FIT config string, load
       addresses
     - Controlling which overlay is selected at boot
   * - ``rcar-customize-extmodules``
     - Add, patch, or re-pin out-of-tree modules: cmemdrv, qos, gles
       (pvrsrvkm)
     - Bumping a module revision or registering a new one
   * - ``rcar-customize-initramfs``
     - Edit the init script, busybox config, bundled PCIe driver and PHY
       firmware
     - NVMe/USB boot fails, or an early-boot tool/firmware is needed
   * - ``rcar-print-build-info``
     - Print current build state: resolved paths, artifacts, sizes, times
     - Answering "what is built right now?"
   * - ``rcar-verify-build``
     - Verify artifacts without a board: fitImage, overlay apply,
       ``modules.dep``, initramfs
     - After any build, before deploying
   * - ``rcar-deploy-image``
     - Back up, rsync fitImage/modules/firmware over ssh, reboot, confirm new
       kernel
     - Pushing a finished build to real hardware
   * - ``rcar-verify-hardware``
     - Check the live board: selected FIT config, overlay nodes, driver
       binding
     - After deploy, or validating a device tree change on hardware

Typical flow:

``rcar-setup-workspace`` -> ``rcar-customize-*`` -> ``rcar-build`` ->
``rcar-verify-build`` -> ``rcar-deploy-image`` -> ``rcar-verify-hardware``

Setting Up the Build Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install the required packages:

.. code-block:: bash

   sudo apt update
   sudo apt install \
       build-essential \
       gcc-aarch64-linux-gnu \
       libc6-dev-arm64-cross \
       bc \
       bison \
       flex \
       cpio \
       kmod \
       curl \
       file \
       libssl-dev \
       libelf-dev \
       libncurses-dev \
       dwarves \
       u-boot-tools \
       git \
       rsync

Create a workspace for the build (you can choose any location and name):

.. code-block:: bash

   mkdir -p ~/rcarv4h_workspace
   cd ~/rcarv4h_workspace

Clone the build scripts:

.. code-block:: bash

   git clone --single-branch --depth 1 --branch ubuntu/rcar-v4h-sh \
       https://github.com/renesas-rdk/rcar-utils.git

The kernel source is not cloned separately. The first kernel build looks for it
in ``rcar-utils/linux-sh`` and, when it is not there, prints the repository and branch it is
about to use and asks before cloning:

.. code-block:: text

   No kernel source found at <rcar-utils>/linux-sh.
     repository: https://github.com/renesas-rdk/linux-sh.git
     branch:     ubuntu/rcar-v4h-sh
   Clone it now? [y/N]

Answering ``y`` clones that one branch. You can also clone it yourself beforehand:

.. code-block:: bash

   git clone --single-branch --branch ubuntu/rcar-v4h-sh \
       https://github.com/renesas-rdk/linux-sh.git rcar-utils/linux-sh

Configuring the Build Script
""""""""""""""""""""""""""""

All build commands are driven by a single entry point, ``rcar-utils/local-build-scripts/main_build.sh``,
and are configured through ``rcar-utils/local-build-scripts/config.ini``.

No configuration is required. Every path is derived from the location of the scripts, so the
repository is ready to build as it is cloned:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Directory
     - Contents
   * - ``rcar-utils/linux-sh/``
     - Kernel source. Cloned on demand, as described above.
   * - ``rcar-utils/workspace/kernel-modules/``
     - Installed kernel modules, their configuration files and the firmware that ships with them.
   * - ``rcar-utils/workspace/ext-modules/``
     - Out-of-tree module sources, fetched at the revisions pinned in ``config.ini``, and their
       own ``downloads/`` cache for the sources released as tarballs.
   * - ``rcar-utils/workspace/arm-trusted-firmware/``
     - TF-A source, with ``release/`` holding the BL31 artifacts built from it.
   * - ``rcar-utils/workspace/initramfs/``
     - busybox tree, the staged ``rootfs/`` and ``uInitramfs.cpio.gz``.
   * - ``rcar-utils/workspace/fitimage/``
     - FIT image inputs and the resulting ``fitImage``.
   * - ``rcar-utils/workspace/downloads/``
     - Download cache. Every file in it is verified against the checksum pinned in ``config.ini``.

``linux-sh/`` and ``workspace/`` are listed in ``.gitignore``, so a build leaves the repository
clean.

To build somewhere else, uncomment the matching path in ``config.ini``. ``KERNEL_URL`` and
``KERNEL_BRANCH`` are the exception: they are not paths and are set, not commented out.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Setting
     - Description
   * - ``KERNEL_DIR``
     - Kernel source tree. Defaults to ``rcar-utils/linux-sh``.
   * - ``KERNEL_URL`` /
       ``KERNEL_BRANCH``
     - Repository and branch used when the kernel source has to be cloned.
   * - ``WORKSPACE_DIR``
     - Parent of every output directory. Defaults to ``rcar-utils/workspace``. Set it to move all
       of them at once.
   * - ``KERNEL_MODULES_OUTPUT_DIR``,

       ``EXT_MODULES_SRC_DIR``,

       ``TFA_SRC_DIR``,

       ``INITRAMFS_SRC_DIR``,

       ``FIT_OUTPUT_DIR``,

       ``DOWNLOAD_DIR``
     - One output directory each, all under ``WORKSPACE_DIR`` by default.
   * - ``TFA_OUTPUT_DIR`` /
       ``INITRAMFS_OUTPUT_DIR``
     - Where the BL31 artifacts and ``uInitramfs.cpio.gz`` are written. Default to
       ``${TFA_SRC_DIR}/release`` and ``INITRAMFS_SRC_DIR``.

The remaining settings can be left at their defaults. These are the ones that are occasionally
worth changing:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Setting
     - Description
   * - ``KERNEL_LOCALVERSION``
     - Suffix appended to the kernel release string reported by ``uname -r``. Defaults to
       ``-arm64-renesas``.
   * - ``BL31_BIN``
     - ARM Trusted Firmware BL31 blob loaded by every FIT configuration. Left unset, it defaults
       to the blob built by the ``bl31`` target, which ``fitimage`` builds itself when it is
       missing. Set it only to use a blob from another build, which is then never rebuilt. See
       :ref:`Building the ARM Trusted Firmware BL31 Blob <build_bl31>`.
   * - ``INITRAMFS_CPIO``
     - Initramfs packaged as the ``initramfs`` FIT configuration. Left unset, it defaults to the
       image built by the ``initramfs`` target. Set it only to use an image from another build,
       which is then never rebuilt. See :ref:`Building the Initramfs <build_initramfs>`.
   * - ``FIT_KERNEL_LOADADDR`` /
       ``FIT_ATF_LOADADDR``
     - Load and entry addresses written into the FIT image. They must match the U-Boot
       environment of the board.
   * - ``CMEM_BSIZE``
     - Memory reserved for ``cmemdrv``, written to ``modprobe.d`` as
       ``options cmemdrv bsize=...``.

The rest are best left as they are shipped: ``PLATFORM`` accepts only ``RCAR-V4H-SH`` on this
branch, ``FIT_ITS`` points at a hand-written image tree source instead of the generated one, and
the ``*_URL`` / ``*_SRCREV`` / ``*_SHA256`` pairs pin the sources the build fetches itself. The
comments in ``config.ini`` describe each of them.

.. important::

   Always run ``main_build.sh`` from the ``local-build-scripts`` directory. The scripts read
   their configuration with ``source ./config.ini``, so they fail if started from anywhere else:

   .. code-block:: bash

      cd ~/rcarv4h_workspace/rcar-utils/local-build-scripts

   Because ``config.ini`` is sourced after the shell environment is set up, every setting that
   it assigns overwrites the environment: to change one of those, edit ``config.ini``. The path
   settings are shipped commented out for that reason, and while a line stays commented out the
   variable can also be set for a single run:

   .. code-block:: bash

      KERNEL_MODULES_OUTPUT_DIR=/tmp/mods ./main_build.sh kernel modules-install

   ``PLATFORM`` is the other exception: ``main_build.sh`` also accepts it as the ``PLAT``
   variable.
