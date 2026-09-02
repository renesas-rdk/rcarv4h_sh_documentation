.. _sample_apps:

Sample Applications
-------------------

This section introduces sample ROS 2 applications developed for the Renesas R-Car V4H SH platform,
demonstrating various functionalities and use cases.

Every application combines a perception front end from the :ref:`Model Zoo <model_zoo>` with a
robot control back end, and every one can be visualized in Foxglove Studio.

.. _sample_apps_prerequisites:

Prerequisites for Running Sample Applications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before running any sample application, complete the following common setup steps:

#. Set up the R-Car V4H SH board as described in the
   :ref:`Quick start guide for R-Car V4H SH <quick_setup_sh_guide>`.

#. Complete the :ref:`Application Development Guide <development_guide>` to set up the
   cross-compilation environment, including the Docker container and the VS Code workspace.

   Run the setup script to create the Docker-based cross-compilation environment:

   .. code-block:: bash

      wget https://github.com/renesas-rdk/ros2_demo_workspace/raw/refs/heads/main/common_utils/setup_rdk_docker.sh
      chmod +x setup_rdk_docker.sh
      ./setup_rdk_docker.sh rcarv4h

   Enter the Docker container:

   .. code-block:: bash

      docker exec -it <container_name> bash

   Replace ``<container_name>`` with the name you chose during setup.

   The sections below assume you already know how to cross-build a ROS 2 application for the
   R-Car V4H SH board, and how to deploy and run it. They only cover the demo-specific steps.

#. Optional: Set up the robot arm or hand according to the instructions in the corresponding
   bringup package if you have the physical robot hardware.

.. tip::

   A physical robot arm or hand is not required for every sample application. Several demos ship a
   mock-hardware mode, and you can use Foxglove Studio to visualize the robot state in a simulated
   environment. See :ref:`Foxglove Visualization <foxglove_visualization>` for details.

Connecting the Demo Hardware
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every peripheral these demos use attaches to the R-Car V4H SH over USB:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Peripheral
     - How it attaches
   * - Cameras
     - USB cameras, and a USB RealSense depth camera for the grasping and chess demos. Each
       appears as a ``/dev/video*`` node.
   * - Robot arm, Ruiyan RH2 hand
     - A USB-to-CAN adapter each, appearing as a ``can*`` network interface.
   * - Inspire RH56 and RH56E2 hands
     - A USB-to-serial adapter, appearing as a ``/dev/ttyUSB*`` node.
   * - Renesas SSC tactile glove
     - SPI or serial, selected by the ``glove_transport`` argument.

.. important::

   The board has two USB Type-A and two USB Type-C ports, and the demos that combine an arm, a
   hand, and one or two cameras need more than that. Use a powered USB hub, and prefer spreading
   the cameras across different root hubs: two uncompressed camera streams on one USB 2.0 root
   hub will drop frames.

Identify each device before launching a demo, because the launch arguments name them explicitly:

.. code-block:: bash

   ls /dev/video*              # cameras
   ls /dev/ttyUSB*             # USB-to-serial adapters
   ip link show | grep can     # USB-to-CAN adapters

.. _sample_apps_deploy:

Deploying and Installing Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After cross-building, the ``install`` folder has to reach the board and the demo's runtime
dependencies have to be installed there. The VS Code workspace does both over SSH, so neither
step needs a terminal on the board.

Using the VS Code Tasks
"""""""""""""""""""""""

Make sure ``TARGET_IP`` in ``settings.json`` points at your board (see
:ref:`Workspace Settings <workspace_settings>`), then run the two tasks in order:

#. **Deploy.** Click the **Deploy** button in the status bar, or press ``Ctrl+Shift+P``, run
   **Tasks: Run Task**, and choose **ROS2: Deploy to Target**. This copies the ``install``
   directory to the board.

#. **Install dependencies.** Click the **Install Deps** button, or run the
   **ROS2: Install Deps on Target (rosdep)** task. It runs ``rosdep`` on the board over SSH
   against the workspace you just deployed.

Both tasks are described in :ref:`ROS 2 VS Code Workspace Configuration <ros2_vscode_workspace>`.

.. tip::

   The **Install Deps** task only has to be re-run when a demo's dependencies change, such as
   after adding a package or editing a ``package.xml``. Re-deploying alone is enough after a
   plain source change.

Doing It Manually
"""""""""""""""""

If you are not using the VS Code workspace, copy the ``install`` folder to the board yourself,
then run this in your ROS 2 workspace on the board:

.. code-block:: bash

   source /opt/ros/jazzy/setup.bash
   rosdep install --from-paths install/*/share -y -r --ignore-src

Running a Demo
^^^^^^^^^^^^^^

Source the workspace on the board before launching any demo:

.. code-block:: bash

   source /opt/ros/jazzy/setup.bash
   source install/setup.bash

The demos can also be started from VS Code with the **Run LaunchFile** and
**Run ExecutableFile** buttons, once the matching package and launch-file variables are set in
``settings.json``. See :ref:`ROS 2 Application Deployment <ros2_deployment>` for that
workflow.

List of Sample Applications
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following table lists the sample applications and the perception package each one uses:

.. list-table::
   :header-rows: 1
   :widths: 32 48 20

   * - Application
     - What it demonstrates
     - Perception
   * - :ref:`Vision-Based Dexterous Hand <sample_app_dexhand>`
     - A dexterous hand mimics the operator's hand in real time from camera input.
     - ``rcar_pose_estimation``
   * - :ref:`Dexterous Hand with Tactile Sensors <sample_app_dexhand_sensors>`
     - Adds a tactile glove and a second camera: grip force adapts to the detected object.
     - ``rcar_yolox``, ``rcar_mediapipe_hand`` (in the ``dexhand_tri_cascade`` node)
   * - :ref:`Rock-Paper-Scissors <sample_app_rps>`
     - Gesture recognition drives a dexterous hand through a full game loop.
     - ``rcar_object_detection``
   * - :ref:`Queen's Hand Chess Robot <sample_app_queens_hand>`
     - A robot arm plays physical chess against a human, driven by a behavior tree.
     - ``rcar_chess_pieces_detection``
   * - :ref:`Vision-Based Grasping <sample_app_grasping>`
     - Pick-and-place of detected objects using a depth camera and a behavior tree.
     - ``rcar_object_detection``

Follow the instructions in the respective sections to run each application on the R-Car V4H SH
platform.

.. toctree::
   :maxdepth: 1

   dexhand
   dexhand_with_sensors
   rock_paper_scissors
   queens_hand
   vision_based_grasping
