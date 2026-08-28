REACTION Usage
""""""""""""""

Once REACTION is installed, running a model always follows the same flow: prepare the target
board, describe the experiment in a ``reaction.yaml`` file, then run ``reaction start`` on the
host machine. The entire pipeline - ONNX export, quantization, TVM compilation for the CNN-IP,
execution on the board and the accuracy or latency report - is driven from that single YAML
file.

Workflow
~~~~~~~~

#. Set up the TVM RPC server on the target board.
#. Activate the REACTION environment on the host.
#. Write ``reaction.yaml`` for the experiment.
#. Run ``reaction start`` on the host.
#. Analyze the results in ``work_dir/``.

.. note::

   The CEVA DSP is not supported in this release on the R-Car V4H SH platform, so
   ``task: tvm_cch`` (CNN-IP + CPU) is the usual choice. The ``tvm_cdh`` and ``tvm_bundle``
   tasks rely on the CEVA DSP and are therefore not available.

Available Models
~~~~~~~~~~~~~~~~

The installation script already unpacks the model input package into the REACTION directory, so
the sample models are available out of the box. The names that can be used in ``model_name`` are
cataloged in the registry files under ``reaction/register/configs``, one per model source:
``hugging_face``, ``openmmlab``, ``torchhub`` and ``custom``, plus
``register/application/config`` for the application models.

Set Up the TVM RPC Server on the Target
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

REACTION runs the compiled model on the board through a TVM RPC server. The server relies on a
private Python 3.10 environment that has to be installed once, as described in
:ref:`Setting Up the RPC Server on the Target Board <rpc-server-setup>`. Start it on the board
before running ``reaction start``, and keep ``rpc_server_auto: false`` in ``reaction.yaml``:

.. code-block:: bash

   # Run this command on the target board
   bash ~/rpc_server/start_rpc_server.sh

Activate the REACTION Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``reaction`` command lives in the virtual environment created by the installation script.
Change into the REACTION root directory and activate it before running any experiment:

.. code-block:: bash

   # Run these commands on the host machine
   cd /opt/rcar-xos/v3.xx.0/tools/hyco/reaction
   source .venv/bin/activate

.. note::

   Adjust the version in the path if a different SDK release is installed. This directory is the
   REACTION root directory: ``reaction.yaml`` and ``work_dir/`` are located here. Leave the
   environment with ``deactivate`` when the work is done.

Run an Experiment
~~~~~~~~~~~~~~~~~

Create a ``reaction.yaml`` file in the REACTION root directory. A minimal configuration for
running a registered model on the board is:

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

See :doc:`reaction_config` for the meaning of these keys. Then run the experiment from the same
directory:

.. code-block:: bash

   # Run these commands from the activated environment
   reaction start              # Accuracy and latency, as configured by action
   reaction start -a latency   # Latency only
   reaction start -a profile   # Profiling

.. tip::

   The configuration does not have to be the ``reaction.yaml`` in the REACTION root directory.
   ``--ryaml`` points ``reaction start`` at a custom-named file, so each experiment can keep its
   own configuration instead of editing the same file over and over:

   .. code-block:: bash

      reaction start --ryaml configs/resnet18_latency.yaml

   Two things to keep in mind: for a BYOM model without Docker dependency, ``--ryaml`` is the
   only argument that can be given, the other options have to come from the file itself. And if
   the file lives outside the REACTION root directory, that directory needs its own ``models``
   folder holding the model to run.

Analyze the Results
~~~~~~~~~~~~~~~~~~~

Results are written to ``work_dir/<experiment_name>``, where the experiment name defaults to the
lowercase ``model_name`` unless ``name`` is set in ``reaction.yaml``. The evaluation summary is
also appended to ``register/summary/summary.csv``. The typical metrics are the mean latency of a
single inference, averaged over 10 repetitions by default, and the accuracy of the model
(Top-1/Top-5 for classification, mAP for object detection, mIoU for semantic segmentation).

A result directory contains the artifacts of each stage:

.. code-block:: text

   work_dir/resnet18
   ├── onnx          # FP32 ONNX model exported from the source model
   ├── quant         # Quantized ONNX model, the input of the compiler
   ├── summary       # evaluate.log and the experiment configuration
   └── tvm-v4x
       └── tvm_cch   # Compilation artifacts, logs and the TVM Relay IR

.. tip::

   ``tvm-v4x/<task>/tvm_model_relay.txt`` contains the TVM Relay Intermediate Representation and
   shows how the model was partitioned. Operators inside
   ``@tvmgen_default_tvmgen_default_rcar_imp_main_xxx`` are dispatched to the CNN-IP; the rest
   runs on the CPU.
