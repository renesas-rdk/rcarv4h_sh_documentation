.. _rcar_object_detection:

Object Detection Applications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``rcar_object_detection`` drives the YOLOv5, YOLOv8, and YOLOX detectors through
:ref:`the rcar_model graph runtime <rcar_model>` and publishes detections and inference timing.
``rcar_chess_pieces_detection`` builds on the same YOLOv8 path and adds board-state
reconstruction.

rcar_object_detection
"""""""""""""""""""""

The package provides four executables that share one model-configuration and launch convention:

.. list-table::
   :header-rows: 1
   :widths: 32 38 12 18

   * - Executable
     - Topology
     - Lanes
     - Default ``model_type``
   * - ``yolov5_object_detection``
     - Multi-lane YOLOv5 (TVM backbone plus ONNX Non-Maximum Suppression (NMS))
     - 4
     - ``yolov5_coco``
   * - ``yolov8_rps_detection``
     - Single-stage YOLOv8
     - 1
     - ``yolov8_rps``
   * - ``yolox_rps_detection``
     - Single-stage YOLOX
     - 1
     - ``yolox_rps``
   * - ``yolox_soft_detection``
     - Single-stage YOLOX for soft objects
     - 1
     - ``yolox_soft``

Parameters
~~~~~~~~~~

The following table lists the node parameters:

.. list-table::
   :header-rows: 1
   :widths: 26 12 20 42

   * - Parameter
     - Type
     - Default
     - Description
   * - ``model_type``
     - string
     - per executable
     - Key in ``config/models/models_config.yaml``.
   * - ``confidence_threshold``
     - double
     - 0.4
     - Detection score threshold. Overrides the value in the YAML file when set.
   * - ``iou_threshold``
     - double
     - from the YAML file
     - NMS Intersection over Union (IoU) threshold. Not used by ``yolov5_object_detection``.
   * - ``processing_queue_size``
     - int
     - 1
     - Drop-oldest depth on the per-lane frame source and on the image subscription QoS history.
   * - ``image_topics``
     - string[]
     - one entry per lane
     - Input topics. The length must match the number of inputs in the ``exec_config.json``.

Topics
~~~~~~

The following table lists the topics the node subscribes to and publishes:

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Topic
     - Direction
     - Type
   * - ``image_topics[lane]``
     - sub
     - ``sensor_msgs/msg/Image``
   * - ``bounding_box`` (``bounding_box_<lane>`` for YOLOv5)
     - pub
     - ``geometry_msgs/msg/PoseArray``
   * - ``inference_timing`` (``inference_timing_<lane>`` for YOLOv5)
     - pub
     - ``diagnostic_msgs/msg/DiagnosticStatus``
   * - ``object_detect``
     - pub
     - ``std_msgs/msg/String``

For the multi-lane YOLOv5 node the lane index is taken from the trailing digits of the model or
input name in the JSON, so ``detect0``, ``nms3``, and ``in2`` map to lanes 0, 3, and 2.

Provided Models
~~~~~~~~~~~~~~~

The following table lists the models shipped with the package:

.. list-table::
   :header-rows: 1
   :widths: 20 30 14 10 26

   * - ``model_type``
     - Classes
     - Confidence
     - IoU
     - Stages
   * - ``yolov5_coco``
     - 80 (COCO)
     - 0.4
     - 0.45
     - ``detect0`` to ``detect3`` (TVM) plus ``nms0`` to ``nms3`` (ONNX)
   * - ``yolov8_rps``
     - 3 (paper, rock, scissor)
     - 0.6
     - 0.3
     - ``detect0`` (TVM)
   * - ``yolox_rps``
     - 3 (paper, rock, scissor)
     - 0.6
     - 0.3
     - ``detect0`` (TVM)
   * - ``yolox_soft``
     - 5 (carrot, coke, egg, pp_cup, sponge)
     - 0.7
     - 0.45
     - ``detect0`` (TVM)

Class names, thresholds, and the graph wiring live in ``config/models/models_config.yaml`` and in
each model's ``config/models/<name>/exec_config.json``. The compiled models ship with the package
under ``config/models/<name>/models/``; every TVM model is compiled with REACTION
``task: tvm_cch``.

Launch Files
~~~~~~~~~~~~

Each launch file brings up its image sources, the detection node, a per-lane bounding-box
visualizer, a timing overlay, and a ``foxglove_bridge`` on port 8765.

.. code-block:: bash

   # Four-lane YOLOv5 on the bundled COCO test images
   ros2 launch rcar_object_detection static_yolov5_4lane.launch.py

   # Single-lane YOLOv8 rock-paper-scissors on a bundled test image
   ros2 launch rcar_object_detection static_yolov8_rps.launch.py

   # Single-lane YOLOX rock-paper-scissors on a bundled test image
   ros2 launch rcar_object_detection static_yolox_rps.launch.py

For the four-lane launch, the outputs are remapped per lane to
``/object_detection/lane<lane>/bounding_box`` and
``/object_detection/lane<lane>/inference_timing``.

To run a node directly with custom settings:

.. code-block:: bash

   # Custom confidence threshold
   ros2 run rcar_object_detection yolov8_rps_detection --ros-args -p confidence_threshold:=0.6

   # Point a single-lane detector at another image topic
   ros2 run rcar_object_detection yolov8_rps_detection \
     --ros-args -p image_topics:="['/camera/image_raw']"

   # Give YOLOv5 its four input topics
   ros2 run rcar_object_detection yolov5_object_detection \
     --ros-args -p image_topics:="['/cam0','/cam1','/cam2','/cam3']"

Adding a Model
~~~~~~~~~~~~~~

#. Place the model artifacts under ``config/models/<name>/``: an ``exec_config.json`` plus a
   ``models/`` subdirectory holding the per-stage TVM and ONNX files it references. The ``file``
   paths in the JSON are relative to the ``exec_config.json`` directory.

#. Add an entry to ``config/models/models_config.yaml``:

   .. code-block:: yaml

      <name>:
        exec_config: "models/<name>/exec_config.json"  # relative to config/
        class_names: [ ... ]
        confidence_threshold: 0.4
        iou_threshold: 0.45
        input_order: rgb   # optional, default 'rgb'; set 'bgr' for BGR-trained models

   Stage names such as ``detect0`` and ``nms1`` are read from the ``models`` section of the JSON
   at startup. Do not declare them in the YAML file. For a ``tvm_cch`` model, also set
   ``input_name`` on its ``models`` entry, as described in
   :ref:`The exec_config.json File <exec_config_schema>`.

#. Rebuild, then run with ``-p model_type:=<name>``.

.. _chess_pieces_detection_pkg:

rcar_chess_pieces_detection
"""""""""""""""""""""""""""

This package runs a 12-class YOLOv8 detector through the same runtime and converts the detections
into a board state expressed as a Forsyth-Edwards Notation (FEN) piece-placement string. The
model, ``yolov8_chess``, is YOLOv8m at 640x640 compiled with REACTION ``task: tvm_cch``.

The executable is ``yolov8_chess_pieces_detection``.

Parameters
~~~~~~~~~~

The following table lists the node parameters:

.. list-table::
   :header-rows: 1
   :widths: 28 12 24 36

   * - Parameter
     - Type
     - Default
     - Description
   * - ``model_type``
     - string
     - ``yolov8_chess``
     - Key in ``config/models/models_config.yaml``.
   * - ``confidence_threshold``
     - double
     - 0.5
     - Detection score threshold.
   * - ``iou_threshold``
     - double
     - 0.45
     - NMS IoU threshold.
   * - ``image_topics``
     - string[]
     - ``["/image_raw"]``
     - One entry per lane.
   * - ``processing_queue_size``
     - int
     - 1
     - Frames buffered per lane.
   * - ``convert_to_fen``
     - bool
     - false
     - Publish ``board_state`` as FEN.
   * - ``board_size_px``
     - double
     - 800.0
     - Canonical board size the homography rectifies to.
   * - ``calibrated_board_file``
     - string
     - ``/tmp/board_square_points.yaml``
     - Square-center calibration the FEN homography is built from.
   * - ``detect_on_service``
     - bool
     - false
     - Run inference only on ``detect_board_state`` instead of on every frame.
   * - ``detect_timeout_s``
     - double
     - 5.0
     - How long a ``detect_board_state`` call waits for its result.

Topics and Services
~~~~~~~~~~~~~~~~~~~

The following table lists the topics and services of the node:

.. list-table::
   :header-rows: 1
   :widths: 32 14 54

   * - Name
     - Kind
     - Type
   * - ``image_topics[i]``
     - sub
     - ``sensor_msgs/msg/Image``
   * - ``bounding_box``
     - pub
     - ``geometry_msgs/msg/PoseArray``
   * - ``inference_timing``
     - pub
     - ``diagnostic_msgs/msg/DiagnosticStatus``
   * - ``board_state``
     - pub
     - ``std_msgs/msg/String``, FEN piece placement, only when ``convert_to_fen`` is set
   * - ``object_detect``
     - pub
     - ``std_msgs/msg/String``
   * - ``detect_board_state``
     - srv
     - ``chess_interfaces/srv/DetectBoardState``, only when ``detect_on_service`` is set
   * - ``get_detected_piece``
     - srv
     - ``chess_interfaces/srv/GetDetectedPiece``

Building
""""""""

Build each package inside the cross-compilation container:

.. code-block:: bash

   cross-colcon-build --packages-up-to rcar_object_detection
   cross-colcon-build --packages-up-to rcar_chess_pieces_detection
