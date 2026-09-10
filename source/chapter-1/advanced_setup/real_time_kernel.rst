.. _real_time_kernel:

Real-Time Kernel
^^^^^^^^^^^^^^^^

The Ubuntu image for the R-Car V4H SH ships with the standard kernel, packaged as
``linux-image-6.18.39-arm64-renesas``. A real-time variant of the same kernel, built with
``CONFIG_PREEMPT_RT=y``, is available as a separate package,
``linux-image-6.18.39-arm64-renesas-rt``.

The two packages are alternatives: installing one removes the other, so the board always runs
either the standard kernel or the real-time kernel, never both. Switching between them is a
matter of installing the package you want and rebooting.

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Kernel
     - Package
     - ``uname -r``
   * - Standard
     - ``linux-image-6.18.39-arm64-renesas``
     - ``6.18.39-arm64-renesas``
   * - Real-time
     - ``linux-image-6.18.39-arm64-renesas-rt``
     - ``6.18.39-arm64-renesas-rt``

Switching to the Real-Time Kernel
"""""""""""""""""""""""""""""""""

Run the following commands **on the target board**:

.. code-block:: bash

   sudo apt update
   sudo apt install linux-image-6.18.39-arm64-renesas-rt

The standard kernel package is removed as part of the installation. Reboot the board to start the
real-time kernel:

.. code-block:: bash

   sudo reboot

After the board has rebooted, log in and confirm that the real-time kernel is running:

.. code-block:: bash

   uname -r

The command should report ``6.18.39-arm64-renesas-rt``.

Switching Back to the Standard Kernel
"""""""""""""""""""""""""""""""""""""

Reinstall the standard kernel package, which removes the real-time one in turn, and reboot:

.. code-block:: bash

   sudo apt install linux-image-6.18.39-arm64-renesas
   sudo reboot

``uname -r`` then reports |kernel_release| again.

.. note::

   To build the real-time kernel from source instead of installing the package, set
   ``KERNEL_VARIANT=preempt-rt`` in the ``rcar-utils`` build scripts. See
   :ref:`Custom Linux Kernel and Device Tree <build_kernel>`.
