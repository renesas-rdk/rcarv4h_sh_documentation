Bringing Your Own Model
"""""""""""""""""""""""

REACTION supports custom ONNX models with Post-Training Quantization (PTQ). The flow has two
halves: quantize and evaluate the model with REACTION, then build the quantized model into a
common application that runs standalone on the board. Quantization alone only produces an ONNX
file; it does not put anything on the target.

Prepare the Scripts
~~~~~~~~~~~~~~~~~~~

Two Python scripts are needed alongside the ONNX model:

- ``preprocess.py`` - prepares the calibration images used during quantization.
- ``accuracy_validation.py`` - runs post-processing and computes the accuracy metric.

Templates for both are provided in the ``model-input-package-<ver>.tar.bz2`` add-on package.

.. note::

   If no pre-processing script is registered, random input is used for quantization. This is
   enough for latency evaluation, but not for accuracy evaluation.

Register the Model
~~~~~~~~~~~~~~~~~~

Register the model with ``reaction bond``, which asks for the model name, weights and scripts:

.. code-block:: bash

   # Run this command from the activated environment, in the REACTION root directory
   reaction bond --with-docker

The command prompts for the model name, the ONNX weights, the pre-processing script, the
packages needed to compute accuracy, the compute type (``cpu``/``gpu``) and the device
(``v4h2``), then builds the BYOM Docker image and appends the entry to
``register/configs/byom/byom_requirements.csv``:

.. code-block:: text

   Enter Model Name: hardnet68ds-ptq
   Enter model weights: models/hardnet68ds/hardnet68ds-fp32.onnx
   Enter path to preprocess images script: models/hardnet68ds/preprocess.py
   ...
   Pip packages: opencv-python-headless==4.6.0.66 torch torchvision msgpack
   Compute [cpu/gpu]: cpu
   Device [v4h2/v4m] (default is 'v4h2'): v4h2
   ...
   Enter path to code for accuracy calculation: models

   Registration complete !!!

.. important::

   When asked for the path to the accuracy calculation code, give the **top-level directory**
   that contains the scripts, model files and dataset folders (for example ``models``), not the
   path to an individual script.

   Typos can be corrected afterwards in ``register/configs/byom/byom_requirements.csv``.

Quantize and Evaluate the Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reference the registered model in ``reaction.yaml``:

.. code-block:: yaml

   experiment:
     model_name: hardnet68ds-ptq        # Name given during registration
     weights: models/hardnet68ds/hardnet68ds-fp32.onnx
     preprocess: models/hardnet68ds/preprocess.py
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

Then start the experiment:

.. code-block:: bash

   # Run these commands from the activated environment, in the REACTION root directory
   reaction start              # Accuracy and latency
   reaction start -a latency   # Latency only
   reaction start -a profile   # Profiling

In a Docker-free installation, the post-processing script is invoked through ``reaction with``
instead:

.. code-block:: bash

   reaction with python3 models/hardnet68ds/accuracy_validation.py \
      -onnx models/hardnet68ds/hardnet68ds-fp32.onnx -ra tvm

.. note::

   Because a custom model name is not part of the REACTION registry, it may be reported as
   invalid during execution. This warning does not affect the run.

The run writes the quantized model to ``work_dir/<experiment_name>/quant/*_quant.onnx``. That
file, in ONNX QDQ format, is the input for the application step below.

Run the Model as an Application on the Board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The evaluation above runs the model through the TVM RPC server, one inference at a time. To let
the model run on the board on its own, with pipelining across threads, build it
into a common application. See :doc:`reaction_sample_app` for a walk-through with one of the
provided sample applications; the steps for a custom model are the same, with an extra
registration. The board itself also has to be prepared once for this flow, see
:ref:`Board Setup <board-app-setup>`.

**Step 1 - Prepare the model folder**

Create a folder for the model under ``models`` in the REACTION root directory:

.. code-block:: text

   models
   └── <CustomModelName>
       ├── exec_config.json                 # Execution configuration
       ├── CMakeLists.txt                   # Build description
       ├── modified_config.json             # Optional
       ├── prepostproc.cc                   # Pre- and post-processing
       └── <CustomModelName>_quant.onnx     # Quantized model, ONNX QDQ format

The ``MobileNet_v1-app`` folder from the ``model-input-package-<ver>.tar.bz2`` add-on package
serves as the reference for all four files:

- ``exec_config.json`` - adjust the quantization values to those of the custom model, and the
  input path if custom test data is used. See :doc:`reaction_config` for the blocks of this file.
- ``CMakeLists.txt`` - can be used as it is, as long as the ``model()`` entries match the
  ``models`` block of ``exec_config.json``.
- ``modified_config.json`` - optional, ``RenesasUserConfig.json`` is used when it is absent.
- ``prepostproc.cc`` - has to be adapted to what the custom model expects and returns.

The quantized model must keep the ``_quant.onnx`` suffix. Copy it from
``work_dir/<experiment_name>/quant/``.

**Step 2 - Register the application model**

Append a line for the model to ``register/application/config/app_models_requirements.csv``:

.. code-block:: text

   ,OD,<CustomModelName>,,models/<CustomModelName>/<CustomModelName>_quant.onnx,not_available=True,,,,,,,custom,,

**Step 3 - Define the test data (optional)**

Without this step the test data of ``MobileNet_v1-app`` is used. To use own images, add a set to
``reaction/app/app.py`` and map the model to it:

.. code-block:: python

   custom_set = {
       "pic1.jpg": "<download_link1>",
       "pic2.jpg": "<download_link2>",
   }

   image_list.update(
       {
           ...
           "<custommodelname>": custom_set,
       }
   )

.. important::

   The key in ``image_list`` must be the model name in **all lowercase**.

**Step 4 - Configure and run**

Switch ``reaction.yaml`` to the application flow. Only ``action: app`` is supported here, and
the TVM RPC server is not used at all:

.. code-block:: yaml

   experiment:
     model_name: <CustomModelName>
     task: tvm_cch            # tvm_cch: CNN-IP + CPU
     action: app
     line: onnx
     target: v4h2
     convert_configs:
       tvm:
         host: <board IP address>
         user: ubuntu
         passwd: ubuntu
         ssh_port: 22
         remove_input_quantize: true     # Recommended for custom models
         remove_output_dequantize: true  # Recommended for custom models

.. code-block:: bash

   # Run this command from the activated environment, in the REACTION root directory
   reaction start

REACTION compiles the model, builds the executable, copies everything to the board, runs it
there and prints the performance metrics. The generated files and the board log are kept under
``work_dir/<model_name>/tvm-<device>/common_application``.

.. tip::

   With ``remove_input_quantize`` and ``remove_output_dequantize`` set to ``true``, the
   quantization and dequantization values are taken from ``exec_config.json`` instead of from
   nodes in the model, which is why those values have to match the custom model.

.. note::

   The accuracy and the performance of a custom model depend entirely on the user-provided
   quantization, pre-processing and post-processing. The flow also assumes that the whole model
   compiles for the TVM runtime; models with nodes that fall back to ONNX Runtime have to follow
   the ``yolo`` or ``ssd`` examples in the add-on package instead.
