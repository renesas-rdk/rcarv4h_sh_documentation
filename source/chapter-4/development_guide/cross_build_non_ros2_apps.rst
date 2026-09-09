.. _cross_build_non_ros2_apps:

Cross-build Non-ROS 2 Applications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The cross-compilation environment provided by the Renesas Docker image can also be used to build non-ROS 2 applications for the R-Car V4H SH platform.

This section describes how to cross-compile a generic CMake-based application using the provided toolchain.

Prerequisites
"""""""""""""

- Complete the :ref:`Cross-compilation Environment Setup <requirements_ros2_cross_build>` section.
- Make sure the Docker container is running and accessible.

Setting up the Environment
""""""""""""""""""""""""""

#. Start and access the Docker container:

   .. code-block:: bash

      docker exec -it ros2_cross_build_container bash

#. (Optional) Connect to the Docker container from VS Code using the **Dev Containers** extension for a better development experience.

   Refer to the :ref:`Cross-compilation Environment Setup <requirements_ros2_cross_build>` section for instructions on how to connect to the Docker container from VS Code.

Install Dependencies into the Sysroot
""""""""""""""""""""""""""""""""""""""

Before building the application, install any required libraries into the ARM64 sysroot using ``arm64-chroot``.

For example, to install common development libraries:

.. code-block:: bash

   arm64-chroot apt update
   arm64-chroot apt install -y <package-name>

.. important::

   The ``arm64-chroot`` command already runs with ``sudo`` privileges. Do not add ``sudo`` to commands executed with ``arm64-chroot``.

   For more details on ``arm64-chroot``, refer to the :ref:`Cross-compilation Usage Guide <cross_build_usage>`.

Build the Application
"""""""""""""""""""""

For CMake-based projects, use the cross-compilation toolchain file provided in the Docker container.

#. Navigate to your project directory:

   .. code-block:: bash

      cd /path/to/your/project

#. Create a build directory and configure with CMake:

   .. code-block:: bash

      mkdir build && cd build

      cmake .. -DCMAKE_TOOLCHAIN_FILE=$TOOLCHAINS_WS/cross.cmake \
               -DCMAKE_BUILD_TYPE=Release

   The ``$TOOLCHAINS_WS/cross.cmake`` toolchain file configures the compiler and sysroot for cross-compilation targeting ARM64.

#. Build the project:

   .. code-block:: bash

      make -j$(nproc)

#. The resulting ARM64 binaries are ready to be deployed to the R-Car V4H SH.

Deploy to Target
""""""""""""""""

Copy the built binaries to the R-Car V4H SH using ``scp`` or another file transfer method.

.. code-block:: bash

   scp ./your_application ubuntu@<TARGET_IP>:/home/ubuntu/

Replace ``<TARGET_IP>`` with the IP address of your R-Car V4H SH board.
