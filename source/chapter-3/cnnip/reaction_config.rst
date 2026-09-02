.. _reaction_config:

REACTION Configuration
""""""""""""""""""""""

``reaction.yaml`` is the entry point of every REACTION run. It describes one experiment: which
model to use, which conversion and compilation path to follow, which target to run on, and what
to measure. ``reaction start`` reads this file from the REACTION root directory
(``/opt/rcar-xos/v3.xx.0/tools/hyco/reaction``) and drives the whole pipeline from it — ONNX
export, quantization, TVM compilation for the CNN-IP, execution on the board over RPC, and the
accuracy or latency report. Changing the flow therefore means editing the YAML file, not the
command line.

.. important::

   This section is only an overview of the most relevant keys. The complete reference is
   delivered with the SDK, in ``/opt/rcar-xos/v3.xx.0/docs/sw/hyco/user_manual``.

Basic Structure
~~~~~~~~~~~~~~~

.. code-block:: yaml

   experiment:
     name: my_test          # Optional
     model_name: ResNet18
     task: tvm_cch
     action: eval
     line: onnx
     target: v4h2
     convert_configs:
       tvm:
         host: <board IP address>   # IP address of the board
         port: 9090                 # Port of the manually started TVM RPC server
         user: ubuntu               # SSH user of the board
         passwd: ubuntu             # SSH password of the board
         rpc_server_auto: false     # The RPC server is started manually on the board

.. list-table:: Experiment Keys
   :header-rows: 1
   :widths: 20 80

   * - Key
     - Description
   * - ``name``
     - Experiment name. Artifacts are generated in ``work_dir/<name>``; defaults to the
       lowercase ``model_name``. Define a new ``name`` when testing variations of the same model.
   * - ``model_name``
     - Exact name of the model in the REACTION registry, or the alias of a registered custom
       model. Names are case-sensitive.
   * - ``task``
     - Conversion and inference stage to run. See the table below.
   * - ``action``
     - What to measure. See the table below.
   * - ``line``
     - Conversion line to follow: ``onnx`` or ``torch``.
   * - ``target``
     - Target board: ``v4h2`` or ``v4m``. Use ``v4h2`` on the R-Car V4H SH platform.
   * - ``target_os``
     - Optional. Target operating system: ``linux`` (default) or ``qnx``.
   * - ``weights``
     - Path to the ONNX weights of a model that is not in the registry, relative to the REACTION
       root directory. Given together with ``model_name`` used as a free alias; see
       :ref:`Bringing Your Own Model <reaction_byom>`.
   * - ``preprocess``
     - Path to the pre-processing script that prepares the calibration images, relative to the
       REACTION root directory. Given together with ``weights``; without it, random input is used
       for quantization, which is enough for latency but not for accuracy.

Tasks
~~~~~

.. list-table:: Supported Tasks
   :header-rows: 1
   :widths: 20 80

   * - Task
     - Description
   * - ``pytorch`` / ``onnxruntime``
     - Evaluate a PyTorch model, or convert it to FP32 ONNX and evaluate.
   * - ``quant_onnx`` / ``quant_pytorch``
     - Quantize an ONNX or PyTorch model and evaluate.
   * - ``tvm_cpu``
     - Compile with TVM and run on the x86 host CPU. Useful as an accuracy reference.
       ``convert_configs`` is not needed for this task.
   * - ``tvm_cch``
     - Compile with TVM and run on CNN-IP + CPU of the board with the TVM runtime. It does not
       use the CEVA DSP, so this is the usual choice on the R-Car V4H SH platform.
   * - ``tvm_cdh``
     - Compile with TVM and run on CNN-IP + CEVA DSP + CPU of the board. The CEVA DSP is not
       supported in this release, so this task is not available on the R-Car V4H SH platform.
   * - ``tvm_bundle``
     - Compile the model into a standalone bundle covering all three compute units. It relies on
       the CEVA DSP, which is not supported in this release, so this task is not available on the
       R-Car V4H SH platform.

Actions
~~~~~~~

.. list-table:: Supported Actions
   :header-rows: 1
   :widths: 20 80

   * - Action
     - Description
   * - ``eval``
     - Default. Conversion and inference on the target backend, reporting accuracy and latency.
   * - ``latency``
     - Measure latency only.
   * - ``profile``
     - Collect performance metrics with the profiler.
   * - ``app``
     - Run through the common application, selecting the core automatically.
   * - ``opt``
     - Search for the best quantization parameters.

Conversion Options
~~~~~~~~~~~~~~~~~~

``convert_configs`` holds the per-stage options of the conversion pipeline, grouped by stage:

- ``onnxruntime`` — ONNX export options such as ``opset_version``, ``input_shape``,
  ``input_names`` and ``output_names``, and the manual ``partition`` edges for layers that the
  compiler cannot handle and that must run in ONNX Runtime on the host CPU.
- ``quantization`` — calibration settings such as ``calibration_method``, ``calib_data_root``
  and ``dataset_samples``, the data types ``weight_type`` and ``activation_type``, and
  ``nodes_to_exclude`` to keep selected nodes in floating point.
- ``tvm`` — board connection (``host``, ``port``, ``user``, ``passwd``, ``rpc_server_auto``) and
  compilation settings such as ``target``, ``opt_level``, ``timeout``, ``cnnip_batch_size`` and
  ``cnnip_skip_layers``.

A typical configuration only needs the board connection:

.. code-block:: yaml

   experiment:
     model_name: ResNet18
     task: tvm_cch
     action: eval
     line: onnx
     target: v4h2
     convert_configs:
       tvm:
         host: <board IP address>   # IP address of the board
         port: 9090                 # Port of the manually started TVM RPC server
         user: ubuntu               # SSH user of the board
         passwd: ubuntu             # SSH password of the board
         rpc_server_auto: false     # The RPC server is started manually on the board

.. _reaction_application_options:

Application Options
~~~~~~~~~~~~~~~~~~~

With ``action: app`` the model is not evaluated over the RPC server but built into a common
application that runs standalone on the board, see :ref:`REACTION Sample Application <reaction_sample_app>`. The ``tvm`` stage
then takes a few additional keys:

.. list-table:: Application Keys under ``convert_configs.tvm``
   :header-rows: 1
   :widths: 30 70

   * - Key
     - Description
   * - ``ssh_port``
     - SSH port of the board, ``22`` by default. ``rpc_server_auto`` and ``port`` are not used in
       this flow.
   * - ``remove_input_quantize``
     - Remove the quantize node next to the input. ``true`` by default and required for the
       provided applications; the scale and zero-point are then taken from ``exec_config.json``.
       See :ref:`Reading the Quantization Values from the Model <reading_quant_values>`.
   * - ``remove_output_dequantize``
     - Same for the dequantize node next to the output.
   * - ``skip_mean_quantization``
     - Skip the quantization of mean nodes. Needed by ``ResNet50-app``, where it is the default.
   * - ``keep_app_folder``
     - Keep the ``app_temp/`` output folder on the board after the run. ``false`` by default.
   * - ``convert_argmax``
     - Convert an argmax node to ``int8`` or ``int16``. Empty by default.
   * - ``custom_node_config_path``
     - Path to the custom node configuration, needed by the ``custom_node`` applications. The
       files are under ``configs/custom_node/``.

.. _reaction_exec_config:

The ``exec_config.json`` File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While ``reaction.yaml`` describes *which* model is compiled and for which target,
``exec_config.json`` describes *how* the generated application runs on the board: how many
frames and threads, which model libraries are loaded, which images are fed in, how the
quantization values are applied, how the blocks are wired together. Every application folder
under ``models/`` carries its own copy, and the generator parses it at build time, so the
application has to be rebuilt with ``reaction start`` after every change.

The file has seven mandatory blocks:

.. code-block:: json

   {
     "app-opts":     { },
     "compile-opts": { },
     "inputs":       { },
     "outputs":      { },
     "models":       { },
     "connections":  [ ],
     "threads":      [ ]
   }

The last block is the threading block; its key is ``steps``, ``threads`` or ``workers``. The
example below is the complete configuration of ``MobileNet_v1-app`` reduced to a single thread:

.. code-block:: text

   {
     "app-opts": {
       "frame_per_loop": 1,           // Frames processed per loop, match the thread count
       "number_of_loops": 100,        // Number of loops
       "warmup": true                 // Discard a first warm-up run
     },
     "compile-opts": {
       "threads": 1,                  // Number of threads the application is built for
       "stream_input": false,         // true to read the images from a folder continuously
       "print_inference": false       // true to print the inference results as well
     },
     "inputs": {
       "in0": {
         "file": "mobilenet_v1-app/test_data/cat.jpg",
         "quantize": { "scale": 0.01865844801068306, "zero": -14 }
       }
     },
     "outputs": {
       "out0": [ { "dequantize": { "scale": 0.003920175600796938, "zero": -128 } } ]
     },
     "models": {
       "dsp0": { "file": "mobilenet_v1-app/models/model_dsp0.so", "runtime": "tvm" }
     },
     "connections": [
       "in0[0]  -> dsp0[0]",
       "dsp0[0] -> out0[0]"
     ],
     "threads": [ "dsp0" ]
   }

.. note::

   The comments above are for reading only, JSON does not allow them.

.. list-table:: Blocks of ``exec_config.json``
   :header-rows: 1
   :widths: 20 80

   * - Block
     - Content
   * - ``app-opts``
     - Runtime options: ``frame_per_loop``, ``number_of_loops`` and ``warmup``.
   * - ``compile-opts``
     - Build-time options: ``threads``, ``stream_input``, ``print_inference``, and for the
       visualization applications ``video_name`` and ``display_output``.
   * - ``inputs``
     - One entry per input node. ``file`` for a single image or ``folder`` for continuous input,
       plus the ``quantize`` ``scale`` and ``zero`` of the removed input quantize node. The paths
       are resolved from the directory the application is launched in on the board, so they carry
       the application folder name, as in ``mobilenet_v1-app/test_data/cat.jpg``.
   * - ``outputs``
     - One entry per output node, with the ``dequantize`` ``scale`` and ``zero`` of the removed
       output dequantize node.
   * - ``models``
     - One entry per model library: ``file`` is the path of the ``.so`` or ONNX file, written the
       same way as the ``inputs`` paths (``mobilenet_v1-app/models/model_dsp0.so``), ``runtime``
       is ``tvm`` or ``onnx``.
   * - ``connections``
     - Wiring between the three blocks above, see below.
   * - ``threads``
     - Execution plan, see below. The key is ``steps``, ``threads`` or ``workers``.

**Connections**

A connection has the form ``<source>[index] -> <destination>[index]``, where the source is an
input or a model, and the destination is a model or an output. The index selects the connection
point and is only different from ``0`` for models with several inputs or outputs:

.. code-block:: json

   "connections": [
     "in0[0]   -> dsp0[0]",
     "dsp0[1]  -> post0[0]",
     "dsp0[0]  -> post0[1]",
     "post0[0] -> out0[0]"
   ]

**Threading**

The threading block decides how the elements are scheduled. The three keywords can be nested
freely, but ``workers`` has to be at the root when it is used:

.. list-table:: Threading Keywords
   :header-rows: 1
   :widths: 20 80

   * - Keyword
     - Behavior
   * - ``steps``
     - One thread, elements executed one after the other. For a model whose input is the output
       of the previous one, for example ``"steps": [ "dsp0", "nms0" ]``.
   * - ``threads``
     - Several threads in parallel, treated as one unit: the run is finished when all elements
       are finished. For models that process the same frame, for example
       ``"threads": [ "mobv1", "mobv2" ]``.
   * - ``workers``
     - Several independent threads, each finishing on its own. For identical pipelines on
       different frames, for example four ``{ "steps": [ "dspN", "postN" ] }`` entries.

Keep ``frame_per_loop`` and the number of entries in ``models`` aligned with
``compile-opts.threads``: in the simple case of one input and unsplit models, all three have the
same value.

The ``CMakeLists.txt`` File
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next to ``exec_config.json``, every application folder holds a ``CMakeLists.txt`` that tells the
generator which model libraries to build into the application. It consists of one ``model()``
entry per model, and those entries have to match the ``file`` entries of the ``models`` block:

.. code-block:: cmake

   model(model_dsp0)
   model(model_dsp1)
   model(model_dsp2)
   model(model_dsp3)

The provided applications are built for four threads, one model library per thread. Reducing the
application to a single thread therefore means keeping a single entry:

.. code-block:: cmake

   model(model_dsp0)

For an application that runs several different models, name each one after its ONNX model
instead:

.. code-block:: cmake

   model(models/<your-onnx-model-name>)

.. important::

   The reference of both files is delivered with the SDK, in
   ``reaction/app/generator/docs/execution_configuration.md`` and
   ``reaction/app/generator/docs/model_specific_cmakelists.md``.

Enabling Debug Logs
~~~~~~~~~~~~~~~~~~~

The log level defaults to ``INFO``. Set it to ``DEBUG`` under ``deploy_configs`` to trace each
step of the execution:

.. code-block:: yaml

   experiment:
     deploy_configs:
       log_level: DEBUG

The additional logs appear on the terminal and in
``work_dir/<experiment_name>/tvm-v4h2/<task>/conversion.log`` and ``validation.log``.

.. tip::

   With the YAML extension installed in VS Code, adding ``"configs/schema.json": "reaction.yaml"``
   to ``yaml.schemas`` in ``settings.json`` enables auto-completion and model-name suggestions
   from the registry. The schema path is relative to the ``reaction`` folder, so VS Code must be
   opened inside it.
