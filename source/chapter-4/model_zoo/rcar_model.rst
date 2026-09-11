.. _rcar_model:

The rcar_model Framework
^^^^^^^^^^^^^^^^^^^^^^^^

``rcar_model`` is the base library every model package and every application in the Model Zoo
builds on. It wraps the vendor TVM runtime behind three small concepts so that a ROS 2 node can
run one or more models described by a JSON file without touching the runtime.

Mental Model
""""""""""""

A **graph** is a JSON file (``exec_config.json``) that names some inputs, some models, and how
they connect. You give ``rcar_model`` three callbacks and it does the rest: load the ``.so``
artifacts, start a worker thread, pull frames, run inference, and dispatch results. The
following table lists the three concepts and who supplies each one:

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Concept
     - What it is
     - Who provides it
   * - ``BaseModel``
     - Subclass with ``preprocess()`` and ``postprocess()``. One per model in the JSON.
     - You
   * - ``FrameSource``
     - Where frames come from. Use ``QueueFrameSource`` and ``push()`` for a camera, or one of the
       tagged variants for cascade stages.
     - You
   * - ``start_graph(json, session)``
     - Reads the JSON, wires your callbacks, and returns a ``GraphHandle``. The destructor stops
       the graph cleanly.
     - Library

The library routes work by name: the strings in the JSON (``models.<name>``, ``inputs.<port>``)
are what your callbacks see. Renaming or rewiring in the JSON needs no code changes.

Public Headers
""""""""""""""

The following table lists the public headers and what each one declares:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Header
     - Contents
   * - ``rcar_model/base_model.hpp``
     - The ``BaseModel`` abstraction to subclass.
   * - ``rcar_model/frame_source.hpp``
     - ``FrameSource`` plus the queue, tagged, and multi-input variants.
   * - ``rcar_model/graph_runner.hpp``
     - ``start_graph(...)``, ``GraphHandle``, and ``GraphSession``.
   * - ``rcar_model/tvm_model.hpp``
     - ``TvmModel``, a direct synchronous ``.so`` loader that does not use a graph JSON.
   * - ``rcar_model/model_input.hpp``
     - ``ModelInput``: image and ROI, tensor, or text.
   * - ``rcar_model/model_result.hpp``
     - ``ModelResult``, ``KeyPoint``, ``KeyPointResult``.
   * - ``rcar_model/model_shape_info.hpp``
     - ``ModelShapeInfo``: shape, dtype, quantization parameters, and input role.
   * - ``rcar_model/utils.hpp``
     - NMS and quantization/float conversion helpers.
   * - ``rcar_model/logging.hpp``
     - ``MODEL_INFO`` / ``MODEL_DEBUG`` / ``MODEL_WARN`` / ``MODEL_ERROR`` macros.

Using the Framework from a ROS 2 Node
"""""""""""""""""""""""""""""""""""""

#. Subclass ``BaseModel`` for each model the JSON declares.
#. Create a ``FrameSource`` and feed it from your image callback.
#. Fill a ``GraphSession`` with the three callbacks and call ``start_graph()``.

.. code-block:: cpp

   auto src = std::make_shared<rcar_model::QueueFrameSource>();

   rcar_model::GraphSession session;

   // Per models.<name> in the JSON: return the BaseModel subclass for it.
   session.make_model = [](const std::string & model_name) {
     return std::make_unique<MyDerivedModel>();
   };

   // Per inputs.<port> in the JSON: return the FrameSource feeding it.
   session.make_input = [src](const std::string & input_name) { return src; };

   // Per result produced. model_name matches the JSON key.
   session.on_result = [](const std::string & model_name, auto r) { /* publish */ };

   auto graph = rcar_model::start_graph("/path/to/exec_config.json", std::move(session));

   // In the image callback, push frames; the runner pulls them.
   src->push(rcar_model::ModelInput{frame, cv::Rect(0, 0, frame.cols, frame.rows)});

The ``GraphHandle`` destructor stops the runner and releases the process singleton. Explicit
``graph->stop()`` and ``graph->join()`` are also available.

Relative paths inside the JSON (``inputs.<k>.file``, ``models.<k>.file``) resolve against the
JSON's own directory, so no working-directory setup is required.

Choosing a Frame Source
~~~~~~~~~~~~~~~~~~~~~~~

The following table lists the frame sources and when to use each one:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Source
     - Use when
   * - ``QueueFrameSource``
     - Single camera feeding a single-input model.
   * - ``TaggedFrameSource<Tag>``
     - Cascade stage where the input carries per-frame metadata (header, source bounding box)
       that the result callback has to pair with the output.
   * - ``MultiInputFrameSource``
     - Single producer feeding a model with more than one input.
   * - ``MultiInputTaggedFrameSource<Tag>``
     - Both of the above: a cascade stage feeding a multi-input model.

All variants use a bounded queue with a drop-oldest policy. Call ``set_max_depth(1)`` to keep
only the most recent frame, which is the behavior real-time pipelines need.

Direct Module Loading
~~~~~~~~~~~~~~~~~~~~~

For a fixed model cascade driven from your own control loop, the streaming graph runner is a poor
fit. ``TvmModel`` is a minimal synchronous loader for a single self-contained TVM ``.so``:

.. code-block:: cpp

   rcar_model::TvmModel model("/path/to/model.so");
   model.set_input_float(0, state.data(), state.size());
   model.run();
   std::vector<float> action(model.output_numel(0));
   model.get_output_float(0, action.data(), action.size());

All input and output is float32; the compiled ``.so`` keeps its input ``QuantizeLinear`` and
output ``DequantizeLinear`` nodes in-graph. The TVM dependency is hidden behind a PIMPL, so
consumers can ``find_package(rcar_model)`` and link ``librcar_model.so`` without pulling in TVM
headers.

.. _exec_config_schema:

The exec_config.json File
"""""""""""""""""""""""""

``start_graph()`` takes the path to an ``exec_config.json`` and builds the whole pipeline from it:
which artifacts to load, how they are wired, and how many threads run them. The file is produced
by the REACTION compile pipeline; :ref:`The exec_config.json File <reaction_exec_config>`
describes each block from the authoring side.

What matters when you drive the file from ``rcar_model`` is that the names in the JSON are the
contract between the file and your code. Every key under ``inputs`` and ``models`` is handed
back to one of your three callbacks as a string, so rewiring the graph is a JSON edit, not a code
change.

A Single-Model Graph
~~~~~~~~~~~~~~~~~~~~

This is the complete configuration shipped for the ``yolox_rps`` model of
:ref:`rcar_object_detection <rcar_object_detection>`:

.. code-block:: json

   {
     "app-opts":     { "frame_per_loop": 1, "number_of_loops": 1, "warmup": true },
     "compile-opts": { "threads": 1, "stream_input": true,
                       "print_inference": true, "display_output": false },
     "inputs": {
       "in0": { "quantize": { "scale": 0.9607843160629272, "zero": -128 } }
     },
     "outputs": {
       "out0": [
         { "dequantize": { "scale": 0.018648216500878334, "zero": -63 } },
         { "dequantize": { "scale": 0.018924998119473457, "zero": -42 } },
         { "dequantize": { "scale": 0.020282510668039322, "zero": -41 } }
       ]
     },
     "models": {
       "detect0": { "file": "models/model_detect0.so", "runtime": "tvm", "input_name": "images" }
     },
     "connections": [
       "in0[0] -> detect0[0]",
       "detect0[0] -> out0[0]",
       "detect0[1] -> out0[1]",
       "detect0[2] -> out0[2]"
     ],
     "workers": [ "detect0" ]
   }

One input port, one model, one output port carrying three tensors. The three ``dequantize``
entries under ``out0`` exist because three ``connections`` edges land on it; that count has to
match.

The optional ``input_name`` field binds the frame your application feeds to the model's graph
input by name, here the ``images`` input of the exported YOLOX model. Without it the frame goes to
input index 0. Set it for artifacts compiled with REACTION ``task: tvm_cch``: that task can expose
some of the model's constant tensors as extra graph inputs, so index 0 is not necessarily the
image. Every TVM model shipped in the Model Zoo sets it.

The ``quantize`` and ``dequantize`` scales are in this file rather than in the model because the
artifacts are compiled with ``remove_input_quantize`` and ``remove_output_dequantize`` set, which
strips those nodes from the graph. The runtime applies the values from here instead, so they have
to match the model they were compiled with.
:ref:`Reading the Quantization Values from the Model <reading_quant_values>` below shows how to
recover them, and :ref:`Application Options <reaction_application_options>` covers the REACTION
settings that produce them.

How the Names Reach Your Callbacks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following table maps each JSON key to the callback that receives its name:

.. list-table::
   :header-rows: 1
   :widths: 26 30 44

   * - JSON key
     - Callback
     - What you return or receive
   * - ``inputs.<port>``
     - ``make_input("<port>")``
     - The ``FrameSource`` that feeds this port. Called once per port at startup.
   * - ``models.<name>``
     - ``make_model("<name>")``
     - The ``BaseModel`` subclass for this stage, already configured with its thresholds and
       class names. Called once per model at startup.
   * - ``models.<name>``
     - ``on_result("<name>", result)``
     - The result this stage produced. Called once per inference, per terminal stage.

For the graph above, ``make_input()`` is called with ``"in0"``, ``make_model()`` with
``"detect0"``, and every inference arrives at ``on_result`` tagged ``"detect0"``.

A Two-Lane Cascade
~~~~~~~~~~~~~~~~~~

Because only one graph can run per process, a cascade lives inside a single file. The
MediaPipe cascade of :ref:`rcar_pose_estimation <rcar_pose_estimation>` declares two ports and
two models, abridged here to the name-bearing keys:

.. code-block:: json

   {
     "inputs":  { "in0": { }, "in1": { } },
     "models": {
       "mediapipe_det":      { "file": "models/mediapipe_hand_detector/model.so",
                               "runtime": "tvm", "input_name": "image" },
       "mediapipe_landmark": { "file": "models/mediapipe_hand_landmark/model.so",
                               "runtime": "tvm", "input_name": "input_1" }
     },
     "connections": [
       "in0[0] -> mediapipe_det[0]",
       "mediapipe_det[0] -> out0[0]",
       "mediapipe_det[1] -> out0[1]",
       "in1[0] -> mediapipe_landmark[0]",
       "mediapipe_landmark[0] -> out1[0]",
       "mediapipe_landmark[1] -> out1[1]",
       "mediapipe_landmark[2] -> out1[2]",
       "mediapipe_landmark[3] -> out1[3]"
     ],
     "workers": [ "mediapipe_det", "mediapipe_landmark" ]
   }

The node's ``make_model()`` dispatches on those two names to return a palm detector or a landmark
model, and ``make_input()`` returns a different ``FrameSource`` for ``in0`` and ``in1``: the camera
feeds ``in0``, and the detector's result callback pushes the cropped hand into the source behind
``in1``. Listing both stages under ``workers`` schedules them as independent threads, so the
landmark stage works on one frame while the detector works on the next. Each stage loads its own
``.so``; edit the ``models.<name>.file`` paths to swap in another variant.

.. _reading_quant_values:

Reading the Quantization Values from the Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because the ``QuantizeLinear`` and ``DequantizeLinear`` nodes are stripped from the compiled
artifact, the only place their parameters survive is the quantized ONNX model REACTION produced
on the way there. Read them off that file and copy them into ``exec_config.json``.

#. Locate the quantized model. ``reaction start`` writes it to
   ``work_dir/<experiment_name>/quant/*_quant.onnx`` in ONNX QDQ format. See
   :ref:`Bringing Your Own Model <reaction_byom>` for the run that produces it.

#. Open `Netron <https://netron.app>`_ in your browser and load the ``*_quant.onnx`` file.
   Nothing is uploaded; the viewer parses the model locally in the browser. The desktop build of
   Netron works the same way.

#. Find the ``QuantizeLinear`` node directly after each model input. Select it, and the sidebar
   shows its three inputs: the tensor, the scale, and the zero point. The scale and zero point are
   constant initializers, so their values are shown right there.

#. Find the ``DequantizeLinear`` node directly before each model output and read its scale and
   zero point the same way.

#. Copy the values into the matching blocks:

   .. list-table::
      :header-rows: 1
      :widths: 30 30 40

      * - Netron node
        - Value
        - ``exec_config.json`` field
      * - ``QuantizeLinear`` at an input
        - ``y_scale``
        - ``inputs.<port>.quantize.scale``
      * - ``QuantizeLinear`` at an input
        - ``y_zero_point``
        - ``inputs.<port>.quantize.zero``
      * - ``DequantizeLinear`` at an output
        - ``x_scale``
        - ``outputs.<port>[i].dequantize.scale``
      * - ``DequantizeLinear`` at an output
        - ``x_zero_point``
        - ``outputs.<port>[i].dequantize.zero``

.. important::

   For a model with several outputs, the order of the entries in the ``outputs.<port>`` array is
   not the order in which the nodes appear in Netron. The entry at index ``i`` corresponds to
   ``connections`` edge ``i`` landing on that port, so walk the ``connections`` list and match
   each edge to the output tensor it carries.

.. tip::

   A quick sanity check on an image input: a scale of ``0.003921569`` with a zero point of
   ``-128`` is ``1/255`` on an ``int8`` range, which maps pixel values 0 to 255 onto the ``0.0``
   to ``1.0`` the model was trained on. The MediaPipe cascade above uses exactly that. A scale
   that is orders of magnitude away from what the preprocessing produces is the usual sign that
   the values were copied from the wrong model.

.. warning::

   These values belong to one specific compiled artifact. Recompiling the model (a new
   calibration set, different quantization settings, or a changed ``reaction.yaml``) produces new
   scales, so re-read them from the new ``*_quant.onnx`` whenever you replace a ``.so``. Stale
   values do not fail loudly; the model runs and returns quietly wrong numbers.

What the Runtime Overrides
~~~~~~~~~~~~~~~~~~~~~~~~~~

``rcar_model`` streams frames from a live source for as long as the graph handle exists, so it
ignores or overrides the fields that describe a fixed offline run. The validator still requires
them, so keep them in the file exactly as the compile pipeline produced them:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Field
     - What the runtime does with it
   * - ``app-opts.number_of_loops``
     - Overridden with the maximum value: the graph runs until the handle is destroyed.
   * - ``compile-opts.stream_input``
     - Overridden with ``true``.
   * - ``inputs.<port>.file`` / ``.folder``
     - Skipped. Frames come from your ``FrameSource``, not from disk.
   * - ``app-opts.frame_per_loop``, ``app-opts.warmup``
     - Parsed, then never read.
   * - ``compile-opts.threads``, ``.print_inference``, ``.display_output``
     - Not parsed at all. Thread count comes from the ``workers`` block.

Everything else is read and acted on: the ``inputs`` and ``outputs`` port keys and their
quantization parameters, the ``models`` entries, ``connections``, and the threading block.

Rules
~~~~~

The following rules apply to every ``exec_config.json``:

- Paths in ``models.<name>.file`` and ``inputs.<port>.file`` resolve against the directory holding
  the JSON, so no working-directory setup is required.
- The length of an ``outputs.<port>`` array must match the number of ``connections`` edges landing
  on that port.
- ``outputs.<port>[i]`` may be ``{}`` when that tensor needs no dequantization.
- ``models.<name>.input_name`` is optional. Set it to the graph input that receives the frame
  whenever the compiled model has more than one graph input, as ``tvm_cch`` artifacts can.
- ``workers``, ``steps``, and ``threads`` are mutually exclusive at the top level. The shipped
  R-Car configurations use ``workers``.

To port a new model, copy the closest existing ``exec_config.json``, keep the overridden fields
verbatim, and edit the ports, models, and connections to match your topology. The quantization
and dequantization scales are not yours to invent: they come from the REACTION ``reaction.yaml``
used to compile the artifacts.

Timing Semantics
""""""""""""""""

``ModelResult`` carries three timing values per inference. They deliberately measure different
windows:

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Field
     - What it measures
   * - ``preprocess_ms``
     - Work-only wall-clock of the preprocess hook and the input tensor write for the terminal
       stage. It excludes the blocking wait in ``FrameSource::next()``, and is ``0`` for pure
       model-to-model stages. Use it to profile your own preprocessing code.
   * - ``inference_ms``
     - Cascade-cumulative wall-clock: this stage's run plus every transitive upstream stage's
       run. For a YOLOv5 backbone to NMS lane this is the sum of both stages.
   * - ``postprocess_ms``
     - Wall-clock around the postprocess hook, for the terminal stage only.

The cascade sum applies to model-to-model edges declared in ``connections``. Stages that
application code chains through separate ``FrameSource`` pushes are independent graphs from the
runtime's point of view, so each reports its own ``inference_ms``.

None of the three fields covers the wait for the next input. For end-to-end latency, compare
publish timestamps in your ``on_result`` callback instead.

Limitations
"""""""""""

.. important::

   **One graph at a time per process.** The runner shares process-global state, so two
   ``GraphHandle`` instances cannot run concurrently. Express multiple lanes (cascades,
   multi-camera setups, and so on) inside a single ``exec_config.json`` and let ``make_model()``
   and ``make_input()`` route them by name.

In detail:

- **Only one graph may be live at a time.** Two ``GraphHandle`` instances cannot run
  concurrently. Destroying a handle releases all per-graph state, so calling ``start_graph()``
  again once the earlier handle is destroyed does work.
- **BaseModel instances are not thread-safe.** The letterbox state cached during preprocessing
  is read back during coordinate mapping, so one instance must be driven from a single worker. The
  runner already enforces this; it only matters if you call a model manually outside
  ``start_graph()``.

Building
""""""""

Build the framework inside the cross-compilation container described in
:ref:`Cross-compilation Environment Setup <requirements_ros2_cross_build>`:

.. code-block:: bash

   sysroot-rosdep-install
   cross-colcon-build --packages-select rcar_model
