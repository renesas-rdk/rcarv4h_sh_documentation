.. _sample_app_grasping:

Vision-Based Grasping
^^^^^^^^^^^^^^^^^^^^^

The `renesas_vision_based_grasping <https://github.com/renesas-rdk/renesas_vision_based_grasping>`_ package is the top-level launch and configuration package
for the vision-based pick-and-place demo: an Agilex Piper arm with a dexterous hand picks objects
detected by a RealSense camera and drops them in a bin, driven by a BehaviorTree.CPP mission.

On the R-Car V4H SH the detector is ``rcar_object_detection`` running a YOLOX soft-object model.
See :ref:`Object Detection Applications <rcar_object_detection>` for the detector itself.

The package wires together:

- RealSense D4xx camera bringup through ``realsense2_camera``.
- YOLOX soft-object detection on the R-Car V4H SH.
- 3D object-pose extraction from the detections and the aligned depth image
  (``get_object_pose_server``).
- Arm motion servers for pose moves, trajectory planning, and speed control.
- Force-aware and position-only end-effector control servers.
- The behavior-tree engine, the pick-place module plugin, and the mission tree.
- A tree manager exposing start, pause, resume, restart, and stop control.
- Foxglove visualization: bounding-box overlays and an inference-timing overlay.

The package contains no code of its own; its ``CMakeLists.txt`` installs ``launch/``, ``config/``,
and ``trees/`` only.

Launch Files
""""""""""""

The following table lists the launch files and what each one brings up:

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Launch file
     - Purpose
   * - ``perception_realsense_camera_rcar.launch.py``
     - RealSense camera, YOLOX detection through ``rcar_object_detection``, the Foxglove bridge,
       and the bounding-box and inference-timing overlays.
   * - ``behavior_bringup.launch.py``
     - The execute-layer servers (end-effector, move-to-pose, arm speed, object pose, and
       trajectory planning), plus the tree manager and the behavior-tree engine.

Behavior Tree
"""""""""""""

``trees/MainTree.xml`` is the mission the behavior-tree engine loads. ``MainTree`` retries the
pick-and-place mission up to three times, then returns the arm home.

Hardware Setup
""""""""""""""

#. Complete the :ref:`Prerequisites for Running Sample Applications <sample_apps_prerequisites>`.

#. Connect an Intel RealSense D4xx depth camera to the R-Car V4H SH board.

#. Set up the Agilex Piper arm and the dexterous hand using the instructions in their bringup
   packages. The arm and a Ruiyan RH2 hand each attach through their own USB-to-CAN adapter; an
   Inspire hand attaches through a USB-to-serial adapter.

#. Place the objects to be picked within the camera's field of view and the arm's reach, and put
   the drop-off bin in reach as well.

Quick Software Setup Instructions
"""""""""""""""""""""""""""""""""

.. note::

   Run every command below inside the cross-compilation Docker container set up in
   :ref:`Prerequisites for Running Sample Applications <sample_apps_prerequisites>`.

#. Get the ``ros2_demo_workspace`` repository, which carries the manifest for each demo:

   .. code-block:: bash

      cd ~/ros2_ws
      git clone https://github.com/renesas-rdk/ros2_demo_workspace.git

#. Import the repositories this demo needs with the ``vcs`` tool:

   .. code-block:: bash

      vcs import < ./ros2_demo_workspace/rcar-v4h/vcs_manifests/rcar-v4h_vision_based_grasping.target.lock.repos

   Every repository the demo needs is cloned into the ``src/`` folder of the workspace, each
   pinned to the revision the manifest locks.

#. Install the demo's build dependencies into the target sysroot:

   .. code-block:: bash

      arm64-chroot apt update
      sysroot-rosdep-install

#. Cross-compile the workspace. ``renesas_vision_based_grasping`` is hardware-neutral, so its
   dependencies do not pull in an arm-and-hand assembly. Build the application together with the
   assembly you are going to run.

   For the Piper arm and an Inspire RH56E2 hand:

   .. code-block:: bash

      cross-colcon-build --packages-up-to \
        renesas_vision_based_grasping \
        piper_arm_inspire_rh56e2_hand_bringup

   For the Piper arm and a Ruiyan RH2 hand:

   .. code-block:: bash

      cross-colcon-build --packages-up-to \
        renesas_vision_based_grasping \
        piper_arm_ruiyan_hand_bringup \
        ruiyan_rh2_hand_bringup

   ``ruiyan_rh2_hand_bringup`` is listed on its own because it installs the ``ruiyan_rh2_init.sh``
   script that initializes the hand's USB-to-CAN adapter.

#. Deploy the result to the board and install the runtime dependencies there, as described in
   :ref:`Deploying and Installing Dependencies <sample_apps_deploy>`.

Running the Demo
""""""""""""""""

Source the workspace, then bring the stack up in this order, each part in its own terminal.

.. code-block:: bash

   source /opt/ros/jazzy/setup.bash
   source install/setup.bash

#. **Bring up the robot.** Launch the arm and the hand together, using the assembly you built.

   For the Piper arm and an Inspire RH56E2 hand, which attaches through a USB-to-serial adapter:

   .. code-block:: bash

      ros2 launch piper_arm_inspire_rh56e2_hand_bringup \
        piper_arm_inspire_rh56e2_hand_joint_position.launch.py \
        use_mock_hardware:=false camera_mode:=eye_in_hand \
        arm_can_interface:=can2 arm_speed:=40 serial_port:=/dev/ttyUSB0

   For the Piper arm and a Ruiyan RH2 hand, initialize the hand's USB-to-CAN adapter once per
   power cycle first, then launch:

   .. code-block:: bash

      cd ~/ros2_ws
      ./install/ruiyan_rh2_hand_bringup/share/ruiyan_rh2_hand_bringup/setup/ruiyan_rh2_init.sh

      ros2 launch piper_arm_ruiyan_hand_bringup \
        piper_arm_ruiyan_hand_joint_position.launch.py \
        use_mock_hardware:=false camera_mode:=eye_in_hand \
        arm_can_interface:=can2 arm_speed:=40 hand_can_interface:=can3

   ``can2`` and ``can3`` are the interfaces the USB-to-CAN adapters enumerate as, not the onboard
   CAN-FD header. With the adapters plugged in, run ``ip link show | grep can`` to confirm which
   name belongs to the arm and which to the hand, and pass them accordingly. The launch asks for
   your password so it can bring up the arm's CAN interface.

#. **Start the behavior layer.** Match the end-effector mode to the hand you mounted:

   .. code-block:: bash

      # Inspire RH56E2: force-aware end-effector control, the default
      ros2 launch renesas_vision_based_grasping behavior_bringup.launch.py

      # Ruiyan RH2: plain position control
      ros2 launch renesas_vision_based_grasping behavior_bringup.launch.py \
        eef_control_mode:=no_force

   The launch accepts the following arguments:

   .. list-table::
      :header-rows: 1
      :widths: 24 20 56

      * - Argument
        - Default
        - Description
      * - ``eef_control_mode``
        - ``force``
        - Which end-effector server to launch for the mounted hand. ``force`` is the Inspire
          RH56E2 mode-1 force hold; ``no_force`` is plain position control, used by the Ruiyan
          RH2.
      * - ``params_file``
        - \-
        - Override path to a YAML parameter file. Empty uses ``config/params.yaml`` from
          ``renesas_vision_based_grasping``.

#. **Start perception.**

   .. code-block:: bash

      ros2 launch renesas_vision_based_grasping perception_realsense_camera_rcar.launch.py

   This starts the RealSense camera, the YOLOX detector with a confidence threshold of 0.4, the
   Foxglove bridge, and the overlay nodes. The only launch argument is ``yolox_model_type``, which
   defaults to ``yolox_soft``, a model key in the ``config/models/models_config.yaml`` file of
   ``rcar_object_detection``.

The detection topics keep their ``/yolox_soft_objects_detection/`` names, so the behavior layer
works unchanged.

Controlling the Mission
~~~~~~~~~~~~~~~~~~~~~~~

The tree manager exposes a single control service for the mission lifecycle, which accepts start,
pause, resume, restart, and stop. Use it to drive the demo once both halves are running.
