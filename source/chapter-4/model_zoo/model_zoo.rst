.. _model_zoo:

Model Zoo
---------

This section describes the AI model packages available for the R-Car V4H SH platform.

These packages provide a unified C++ framework for deploying AI models optimized with CNN-IP acceleration,
enabling high power-efficiency inference on the R-Car V4H SH architecture.

The models themselves are compiled ahead of time with the REACTION toolchain described in
:ref:`REACTION <reaction_overview>`; the packages below load the resulting artifacts and
expose them as ROS 2 nodes.

Overview
^^^^^^^^

The R-Car V4H SH AI model ecosystem is organized into the following layers:

- **Base framework** (``rcar_model``): C++ library that wraps the TVM runtime behind a small graph
  API. It owns model loading, the worker thread, and result dispatch, so a ROS 2 node runs one or
  more models from a JSON file without touching the runtime directly.
- **Model-specific packages**: each model family (YOLOv5 in ``rcar_yolov5``, YOLOv8 in
  ``rcar_yolov8``, YOLOX in ``rcar_yolox``, MediaPipe hand in ``rcar_mediapipe_hand``) is a separate
  package that extends the base framework with family-specific pre- and post-processing. These are
  pure ML libraries with no ROS 2 dependency.
- **ROS 2 application packages** (``rcar_object_detection``, ``rcar_pose_estimation``,
  ``rcar_chess_pieces_detection``): ROS 2 nodes that combine the model packages with camera or
  static image input and publish detections, keypoints, and inference timing.
- **ROS 2 utilities** (``renesas_model_utils_ros2``): helper functions for integrating the models
  into ROS 2 applications, including model configuration loading, message encoding, and inference
  diagnostics.

Every model package derives from the same ``rcar_model::BaseModel`` interface, and every
application drives its models through the same ``rcar_model::start_graph()`` entry point. Adding a
model family means adding one library; adding a trained model to an existing family usually means
adding configuration only.

Available Packages
^^^^^^^^^^^^^^^^^^

Core Packages
"""""""""""""

The following table lists the packages that every other package in the Model Zoo depends on:

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Package
     - Description
     - License
   * - `rcar_model <https://github.com/renesas-rdk/rcar_model>`_
     - Base framework providing the ``BaseModel`` abstraction, the TVM graph runtime, frame
       sources, and shared utilities for model loading, preprocessing, inference, and
       postprocessing.
     - Apache-2.0
   * - `renesas_model_utils_ros2 <https://github.com/renesas-rdk/renesas_model_utils_ros2>`_
     - ROS 2 helper library shared by every application in the Model Zoo. Loads a model
       configuration into a ``V4HModelConfig`` with ``load_v4h_model_config()``, and provides the
       ``UtilsROS`` encoders and decoders for bounding boxes, oriented bounding boxes, detection
       metadata, inference timing diagnostics, and image conversion.
     - Apache-2.0

Object Detection Model Packages
"""""""""""""""""""""""""""""""

The following table lists the object detection model families:

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Package
     - Description
     - License
   * - `rcar_yolox <https://github.com/renesas-rdk/rcar_yolox>`_
     - YOLOX object detection with axis-aligned bounding boxes. Single-stage TVM model; extends
       ``BaseModel`` with YOLOX-specific pre- and post-processing.
     - Apache-2.0
   * - `rcar_yolov5 <https://github.com/renesas-rdk/rcar_yolov5>`_
     - YOLOv5 object detection as a two-stage graph: a TVM backbone followed by an ONNX NMS
       post-processor. Both stages are paired inside a single ``exec_config.json``.
     - AGPL-3.0
   * - `rcar_yolov8 <https://github.com/renesas-rdk/rcar_yolov8>`_
     - YOLOv8 detection for full-postprocess TVM models. Provides ``YOLOv8Base`` for the family
       and ``YOLOv8Detect`` for object detection; thresholding and NMS run in C++.
     - AGPL-3.0

Hand Model Packages
"""""""""""""""""""

The following table lists the hand-tracking model package:

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Package
     - Description
     - License
   * - `rcar_mediapipe_hand <https://github.com/renesas-rdk/rcar_mediapipe_hand>`_
     - The two MediaPipe hand-tracking stages: a BlazePalm-style palm detector with host-side
       anchor decode and NMS, and a 21-keypoint hand-landmark estimator.
     - Apache-2.0

ROS 2 Application Packages
""""""""""""""""""""""""""

The following packages can be used as examples of how to integrate model packages into ROS 2
applications. You can also refer to the source code of these packages for implementation details
and best practices.

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Package
     - Description
     - License
   * - `rcar_object_detection <https://github.com/renesas-rdk/rcar_object_detection>`_
     - ROS 2 nodes for camera-based and static image object detection using the YOLOv5, YOLOv8,
       and YOLOX models.
     - AGPL-3.0
   * - `rcar_pose_estimation <https://github.com/renesas-rdk/rcar_pose_estimation>`_
     - ROS 2 nodes for hand landmark estimation with two detector-to-landmark cascades.
     - Apache-2.0
   * - `rcar_chess_pieces_detection <https://github.com/renesas-rdk/rcar_chess_pieces_detection>`_
     - ROS 2 node for 12-class chess-piece detection that reconstructs the board state as a
       Forsyth-Edwards Notation (FEN) string.
     - AGPL-3.0

.. note::

   ``rcar_yolov5``, ``rcar_yolov8``, and the applications that link against them inherit the
   AGPL-3.0 license of the upstream Ultralytics models they target. Check the license of every
   package you link into a product.

.. _act_policy_support:

Action Chunking Transformer (ACT) Policy Support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Beyond the perception models listed above, the R-Car V4H SH also runs Action Chunking Transformer
(ACT), a Vision-Language-Action policy for imitation-learning based manipulation. The
policy takes camera images and the current robot state and predicts a chunk of future actions,
which the robot executes directly. It is compiled for the CNN-IP with the same REACTION toolchain
used for every other model in this chapter, and it runs on the board in real time.

ACT is not part of the public Model Zoo. The policy weights, the model configuration, the training
data recipe, and the integration code are not published with this documentation, and none of the
packages listed above contain them.

.. note::

   If you want to evaluate or deploy an ACT policy on the R-Car V4H SH, get in touch so we can
   discuss your use case directly. Open an issue on
   `renesas-rdk <https://github.com/renesas-rdk/rcarv4h_sh_documentation>`_ or contact your
   Renesas representative. Please do not expect implementation details in this documentation.

.. toctree::
   :maxdepth: 1
   :caption: Model Zoo Contents

   rcar_model
   rcar_object_detection
   rcar_pose_estimation
