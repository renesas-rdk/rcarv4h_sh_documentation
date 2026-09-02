.. _rcar_pose_estimation:

Pose Estimation Application
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``rcar_pose_estimation`` provides two detector-to-hand-landmark cascades. Each runs through
:ref:`the rcar_model graph runtime <rcar_model>` as a single in-process graph, and republishes
bounding boxes, 21-point hand landmarks, and per-stage timing. The following table lists the two
executables and the cascade each one runs:

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Executable
     - Cascade
     - Default ``cascade_model_type``
   * - ``yolox_mediapipe_pose_estimation``
     - YOLOX detector to MediaPipe hand landmark
     - ``yolox_mediapipe_cascade``
   * - ``mediapipe_detector_landmark_pose_estimation``
     - MediaPipe palm detector to MediaPipe hand landmark
     - ``mediapipe_hand_detector_landmark_cascade``

Both nodes take a single camera image, run the detector on one lane, crop the detected hand from
the same frame, and feed the landmark stage on a second lane, all inside one
``exec_config.json``. The MediaPipe-detector cascade additionally builds a rotated,
2.5x-scaled hand Region of Interest (ROI) aligned from the wrist to the middle metacarpophalangeal
(MCP) joint before the landmark stage, matching the MediaPipe reference preprocessing.

Topics
""""""

Publisher and subscriber names are relative; the shipped launch files remap them into a
``/pose_estimation/`` namespace.

yolox_mediapipe_pose_estimation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following table lists the topics of this executable:

.. list-table::
   :header-rows: 1
   :widths: 34 14 52

   * - Topic
     - Direction
     - Type
   * - ``image_raw``
     - sub
     - ``sensor_msgs/msg/Image``
   * - ``bounding_box``
     - pub
     - ``geometry_msgs/msg/PoseArray``
   * - ``hand_landmarks``
     - pub
     - ``geometry_msgs/msg/PoseArray``
   * - ``inference_timing_yolox``
     - pub
     - ``diagnostic_msgs/msg/DiagnosticStatus``
   * - ``inference_timing_mediapipe``
     - pub
     - ``diagnostic_msgs/msg/DiagnosticStatus``

mediapipe_detector_landmark_pose_estimation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following table lists the topics of this executable:

.. list-table::
   :header-rows: 1
   :widths: 34 14 52

   * - Topic
     - Direction
     - Type
   * - ``image_raw``
     - sub
     - ``sensor_msgs/msg/Image``
   * - ``bounding_box``
     - pub
     - ``geometry_msgs/msg/PoseArray``
   * - ``palm_keypoints``
     - pub
     - ``geometry_msgs/msg/PoseArray``
   * - ``palm_roi``
     - pub
     - ``geometry_msgs/msg/PoseArray``
   * - ``hand_landmarks``
     - pub
     - ``geometry_msgs/msg/PoseArray``
   * - ``inference_timing_detector``
     - pub
     - ``diagnostic_msgs/msg/DiagnosticStatus``
   * - ``inference_timing_mediapipe``
     - pub
     - ``diagnostic_msgs/msg/DiagnosticStatus``

``bounding_box`` carries the detections encoded through
``renesas_model_utils::UtilsROS::encode_bounding_box_to_poses()``. ``hand_landmarks`` carries the
21 hand keypoints, ``palm_keypoints`` the seven palm keypoints per detection, and ``palm_roi`` the
four rotated-ROI corners per detection in top-left, bottom-left, top-right, and bottom-right
order.

Parameters
""""""""""

The following table lists the node parameters:

.. list-table::
   :header-rows: 1
   :widths: 28 10 12 50

   * - Parameter
     - Type
     - Default
     - Description
   * - ``cascade_model_type``
     - string
     - per executable
     - Key into ``models_config.yaml``.
   * - ``confidence_threshold``
     - double
     - 0.4 / 0.5
     - YOLOX detection confidence, or the palm-detector score threshold applied before
       Non-Maximum Suppression (NMS).
   * - ``iou_threshold``
     - double
     - 0.45 / 0.3
     - Detector NMS Intersection over Union (IoU) threshold.
   * - ``presence_threshold``
     - double
     - 0.5
     - MediaPipe landmark confidence gate, applied inside the landmark stage.
   * - ``processing_queue_size``
     - int
     - 1
     - Drop-oldest depth on the detector frame source and on the image subscription QoS history.
   * - ``mediapipe_queue_depth`` / ``landmark_queue_depth``
     - int
     - 8
     - Drop-oldest depth on the crop queue feeding the landmark lane.
   * - ``smoothing_enabled``
     - bool
     - true
     - Smooth landmarks across frames with an exponential moving average (EMA).
   * - ``smoothing_factor``
     - double
     - 0.7
     - EMA weight between 0 and 1; higher means more smoothing.

The first default in the Default column applies to ``yolox_mediapipe_pose_estimation`` and the
second to ``mediapipe_detector_landmark_pose_estimation``, where they differ.

Launch Files
""""""""""""

Launch either cascade against a static image or a live camera:

.. code-block:: bash

   # YOLOX to MediaPipe cascade
   ros2 launch rcar_pose_estimation static_yolox_mediapipe.launch.py   # static image
   ros2 launch rcar_pose_estimation camera_yolox_mediapipe.launch.py   # live camera

   # MediaPipe palm detector to MediaPipe landmark cascade
   ros2 launch rcar_pose_estimation static_mediapipe_cascade.launch.py  # static image
   ros2 launch rcar_pose_estimation camera_mediapipe_cascade.launch.py  # live camera

Each launch file brings up the image source, the cascade node, Foxglove visualizers for the
bounding box and the 21-point hand skeleton, the per-stage timing overlays, and a
``foxglove_bridge`` on port 8765. The static launch files use the bundled ``config/test/hand.jpg``
image; the camera launch files start ``v4l2_camera`` and take a ``video_device`` argument that
defaults to ``/dev/video0``.

Building
""""""""

Build the package inside the cross-compilation container:

.. code-block:: bash

   cross-colcon-build --packages-up-to rcar_pose_estimation
