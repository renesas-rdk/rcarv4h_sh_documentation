.. _sample_app_queens_hand:

Queen's Hand Chess Robot
^^^^^^^^^^^^^^^^^^^^^^^^

The `renesas_demo_queens_hand <https://github.com/renesas-rdk/renesas_demo_queens_hand>`_ package is the top-level launch, node, and configuration package
for the Queen's Hand chess-playing robot: an Agilex Piper arm fitted with a dexterous hand
physically plays chess against a human, driven by a BehaviorTree.CPP mission with Stockfish as the
game brain.

Perception runs ``rcar_chess_pieces_detection`` on the R-Car V4H SH: a 12-class YOLOv8 detector
turns the camera image into a Forsyth-Edwards Notation (FEN) board state. See
:ref:`rcar_chess_pieces_detection <chess_pieces_detection_pkg>` for the detector itself.

.. note::

   The demo has a hardware-free mode. ``behavior_bringup_mock.launch.py`` runs the whole stack
   with a mock arm and a mock perception node, so you can exercise the game logic and the behavior
   tree without an arm, a hand, or a camera.

Nodes
"""""

The following table lists the executables the package provides:

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Executable
     - Role
   * - ``chess_engine_node.py``
     - Authoritative game state, built on python-chess and Stockfish. Serves the ``/chess/``
       services for board setup, move validation, move update, best move, human-move detection,
       and Portable Game Notation (PGN) handling. Publishes the latched ``/chess/board_state``
       FEN and ``/chess/game_state``.
   * - ``chess_board_geometry_node``
     - Board geometry derived from the probe-teach calibration. Serves
       ``/chess/get_square_pose``, ``/chess/get_capture_bin_pose``, ``/chess/get_promotion_pose``,
       and ``/chess/get_piece_height``.
   * - ``chess_game_manager_node``
     - Game control; drives the behavior-tree engine lifecycle. Serves ``/chess/game_control`` and
       publishes the latched ``/chess/game_paused`` and ``/chess/game_control_result``.
   * - ``chess_opponent_node.py``
     - Software Stockfish opponent for the software-only demo. Serves ``/chess/opponent/enable``.
   * - ``mock_perception_node.py``
     - Camera and detector replacement for hardware-free runs. Serves
       ``/chessboard/detect_board_state``, ``/get_detected_piece``, and ``/mock/play_human_move``.
   * - ``board_teach_calibration_node.py``
     - Interactive probe-teach board calibration. Writes ``calibrated_board.yaml``.
   * - ``chess_move_client.py``
     - Command-line helper with the ``move``, ``human``, ``best``, ``state``, ``reset``, ``pause``,
       and ``resume`` subcommands.

Run the Python nodes with the ``.py`` suffix, for example
``ros2 run renesas_demo_queens_hand chess_move_client.py state``.

Launch Files
""""""""""""

The following table lists the launch files and what each one brings up:

.. list-table::
   :header-rows: 1
   :widths: 44 56

   * - Launch file
     - Purpose
   * - ``behavior_bringup.launch.py``
     - Real hardware: the execute-layer servers, chess game logic, board geometry, game manager,
       and behavior-tree engine. Run the robot bringup and the perception launch separately.
   * - ``behavior_bringup_mock.launch.py``
     - Hardware-free: the same stack with a ros2_control mock arm and ``mock_perception_node``
       instead of the camera and detector.
   * - ``chess_vs_stockfish.launch.py``
     - Software only, with no arm at all: the engine, the Stockfish opponent, the board renderer,
       and Foxglove.
   * - ``chess_perception_realsense_camera_rcar.launch.py``
     - RealSense camera, ``rcar_chess_pieces_detection``, Foxglove bridge and overlays. Run this
       alongside the real bringup.
   * - ``board_teach_calibration.launch.py``
     - Probe-teach calibration of the physical board.

Foxglove layouts live in ``config/foxglove/``.

Hardware Setup
""""""""""""""

The demo uses the following hardware:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Item
     - Purpose
   * - Agilex Piper 6-DOF arm
     - Moves the pieces. Connects through a USB-to-CAN adapter.
   * - Dexterous hand
     - Grips the pieces. The Ruiyan RH2 is recommended for this demo; the Inspire RH56E2 also
       works. Connects through a second USB-to-CAN adapter.
   * - Intel RealSense depth camera
     - Sees the board. Configured by ``config/realsense/realsense_config.yaml``.
   * - Chessboard and pieces
     - A standard 8x8 board, placed within the arm's reach and fully inside the camera's view.
   * - Probe tool
     - Mounted on the arm for the board teach calibration described below.

Complete the :ref:`Prerequisites for Running Sample Applications <sample_apps_prerequisites>`
first. Mount the camera so that all 64 squares are visible and unobstructed, and place the board
so that the arm can reach every square. Both calibrations below assume the board does not move
afterwards.

.. important::

   Run the steps in this order. Each one depends on the previous:

   #. Calibrate :ref:`the board to the robot <queens_hand_board_calibration>` once, and again
      whenever the board moves relative to the arm.
   #. Calibrate :ref:`the camera to the board <queens_hand_camera_calibration>` once per camera
      placement.
   #. Bring up the robot.
   #. Start perception.
   #. Start the demo stack.

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

      vcs import < ./ros2_demo_workspace/rcar-v4h/vcs_manifests/rcar-v4h_queens_hand.target.lock.repos

   Every repository the demo needs is cloned into the ``src/`` folder of the workspace, each
   pinned to the revision the manifest locks.

#. Install the demo's build dependencies into the target sysroot:

   .. code-block:: bash

      arm64-chroot apt update
      sysroot-rosdep-install

#. Cross-compile the workspace:

   .. code-block:: bash

      cross-colcon-build --packages-up-to renesas_demo_queens_hand

#. Deploy the result to the board and install the runtime dependencies there, as described in
   :ref:`Deploying and Installing Dependencies <sample_apps_deploy>`.

.. _queens_hand_board_calibration:

Calibrating the Board to the Robot
""""""""""""""""""""""""""""""""""

The arm needs to know where each square is in its own ``base_link`` frame. That mapping comes from
a probe-teach calibration whose output is a YAML file holding the 64 square centroids. The
geometry node reads it through its ``calibration_file`` parameter, which points at
``config/calibrated_board.yaml`` by default.

If the board has not moved since the shipped calibration was taken, skip to the camera
calibration.

#. Mount the probe tool on the Piper arm.

#. Start the calibration node:

   .. code-block:: bash

      ros2 launch renesas_demo_queens_hand board_teach_calibration.launch.py

#. Switch the arm to teaching mode. Enable the hand's teaching mode first, then the arm's.

#. Move the tool center point (TCP) to the center of each square in turn. The node records each
   centroid from the ``base_link`` to TCP transform.

#. Read the result from ``/tmp/calibrated_board.yaml``, where the node writes it. Override the
   path with the ``output_file`` argument to write it elsewhere.

#. Copy the file into the package's ``config/`` directory and rebuild to make it the default. The
   demo stack also picks up on-disk changes to the file automatically.

.. caution::

   Teaching mode leaves the arm in a state that has to be cleared. Power the Piper arm off and
   back on before running the verification below or starting the demo. The Piper arm may need to
   be recalibrated after a power cycle.

Verifying the Board Calibration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The verification drives the arm to every square in turn, so you can see whether the probe lands
on the square centers.

#. Copy the calibration file into your workspace, inside the cross-build container:

   .. code-block:: bash

      cd ~/ros2_ws/src/apps/renesas_demo_queens_hand/config
      scp ubuntu@<board_ip>:/tmp/calibrated_board.yaml .

#. Generate one probe pose per square. Adjust the paths to match your checkout:

   .. code-block:: bash

      python3 ~/ros2_ws/src/apps/renesas_demo_queens_hand/test/calculate.py \
        ~/ros2_ws/src/apps/renesas_demo_queens_hand/config/calibrated_board.yaml > cmd_probe.txt

#. Launch the arm with the probe end effector at a low speed:

   .. code-block:: bash

      ros2 launch agilex_piper_arm_bringup agilex_piper_native_cartesian_control.launch.py \
        end_effector:=probe speed:=10

#. In a second terminal, send each pose from ``cmd_probe.txt``, replacing the ``pose:`` block with
   that square's entry:

   .. code-block:: bash

      ros2 topic pub --once /agilex_piper_gpio_controller/target_pose geometry_msgs/msg/PoseStamped "
      {
        header: {frame_id: 'base_link'},
        pose: {
          position: {x: 0.2500, y: 0.0261, z: -0.0200},
          orientation: {x: -0.0520, y: 0.9986, z: 0.0000, w: 0.0000}
        }
      }"

The arm should stop at each square center. If it does not, repeat the calibration.

.. _queens_hand_camera_calibration:

Calibrating the Camera to the Board
"""""""""""""""""""""""""""""""""""

The detector reports pieces in image pixels, so it needs to know which pixels belong to which
square. ``chessboard_analyzer`` provides that mapping: it finds the four outer corners of the
board, rectifies it to a top-down view, and writes the center of every square to a calibration
file.

The detector reads that file through its ``calibrated_board_file`` parameter, which defaults to
``/tmp/board_square_points.yaml``, and fits the image-to-board homography to all 64 centers with
RANSAC.

#. Start the perception launch, which brings up the camera and ``chessboard_analyzer``:

   .. code-block:: bash

      ros2 launch renesas_demo_queens_hand chess_perception_realsense_camera_rcar.launch.py

#. Clear the board so that the corner detector sees the board pattern rather than the pieces.

#. Trigger the detection:

   .. code-block:: bash

      ros2 service call /chessboard_analyzer/trigger_calculate_squares std_srvs/srv/Trigger

   On success the node writes ``/tmp/board_square_points.yaml``, holding each square keyed ``a1``
   to ``h8`` with its image-pixel center and its deprojected 3D position.

#. Check the debug images the node saves under ``/tmp/chessboard_analyzer_debug`` to confirm the
   corners were found correctly.

The detector picks the file up as soon as it appears, and re-reads it whenever it changes on disk,
so FEN publishing starts without restarting anything. Until a valid calibration exists the node
warns and skips FEN output; the piece detections themselves are unaffected.

.. note::

   ``chessboard_analyzer`` labels the squares ``a1`` to ``h8`` according to its ``camera_position``
   parameter, which describes where the camera sits relative to the board: ``white`` (the default,
   0 degrees), ``side_left`` (90 degrees), ``black`` (180 degrees), or ``side_right``
   (270 degrees). Set it to match your
   physical setup, otherwise every square is labeled with a rotated name.

   The detector's own square lookup depends on this, so a wrong ``camera_position`` produces a
   board state that looks plausible but is rotated.

Running the Demo
""""""""""""""""

Hardware-Free Run
~~~~~~~~~~~~~~~~~

To exercise the game logic and the behavior tree without any hardware:

.. code-block:: bash

   ros2 launch renesas_demo_queens_hand behavior_bringup_mock.launch.py

For a software-only game with no arm in the graph at all:

.. code-block:: bash

   ros2 launch renesas_demo_queens_hand chess_vs_stockfish.launch.py

Full Demo
~~~~~~~~~

Complete both calibrations, :ref:`board to robot <queens_hand_board_calibration>` and
:ref:`camera to board <queens_hand_camera_calibration>`, before starting the demo. Then bring
the stack up in this order, each in its own terminal.

#. **Bring up the robot.** Initialize the hand's USB-to-CAN adapter first, then launch the arm
   and the hand together, naming the interface of each adapter:

   .. code-block:: bash

      # Ruiyan RH2 hand: initialize its CAN interface once per power cycle
      cd ~/ros2_ws
      ./install/ruiyan_rh2_hand_bringup/share/ruiyan_rh2_hand_bringup/setup/ruiyan_rh2_init.sh

      ros2 launch piper_arm_ruiyan_hand_bringup piper_arm_ruiyan_hand_joint_position.launch.py \
        arm_can_interface:=can2 hand_can_interface:=can3

   ``can2`` and ``can3`` are the interfaces the two USB-to-CAN adapters enumerate as, not the
   onboard CAN-FD header. With both adapters plugged in, run ``ip link show | grep can`` to
   confirm which name belongs to the arm and which to the hand, and pass them accordingly.

#. **Start perception.**

   .. code-block:: bash

      ros2 launch renesas_demo_queens_hand chess_perception_realsense_camera_rcar.launch.py

   This starts the RealSense camera, the chess-piece detector with ``convert_to_fen: true`` and a
   confidence threshold of 0.7, ``chessboard_analyzer``, the board renderer, the Foxglove bridge,
   and the overlay nodes. It accepts the following arguments:

   .. list-table::
      :header-rows: 1
      :widths: 28 26 46

      * - Argument
        - Default
        - Description
      * - ``robot_plays_as``
        - ``white``
        - Which side the robot plays. Sets the board renderer's orientation.
      * - ``model_type``
        - ``yolov8_chess``
        - Model key in the ``config/models/models_config.yaml`` of
          ``rcar_chess_pieces_detection``.
      * - ``calibrated_board_file``
        - ``/tmp/board_square_points.yaml``
        - Square-center calibration written by ``chessboard_analyzer``. Picked up automatically
          when it appears or changes.

#. **Start the demo stack.**

   .. code-block:: bash

      ros2 launch renesas_demo_queens_hand behavior_bringup.launch.py

   This starts the execute-layer servers, ``chess_engine_node``, ``chess_board_geometry_node``,
   ``chess_game_manager_node``, and the behavior-tree engine. It accepts ``initial_fen`` to start
   or resume from a given position, and ``pgn_file`` with ``ply`` to replay a PGN up to a given
   number of half-moves. Sample games are in ``config/pgn/``.

#. **Play.**

   The demo is ready to play chess against a human. Open Foxglove to see the board state, the
   detected pieces, and the 3D pose of each square. Load the
   ``renesas_demo_queens_hand/config/foxglove/chess_demo.json`` layout and control the game from
   its buttons.
