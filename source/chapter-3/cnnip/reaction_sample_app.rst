REACTION Sample Application
"""""""""""""""""""""""""""

This section shows how to prepare the board and run the sample applications shipped with
REACTION as common applications, standalone on the target.

.. _board-app-setup:

Board Setup
~~~~~~~~~~~

``action: app`` cross-compiles the application against the poky sysroot of the xOS SDK and the
OpenCV of the REACTION application image, then runs that binary on the board. On Ubuntu 24.04 it
does not start: Ubuntu ships OpenCV under a different SONAME than the ``libopencv_core.so.409``
the binary was linked against, and the deploy step writes to ``/home/root`` while running from
the home directory of the SSH user.

``setup_ubuntu_board_for_hyco.sh`` of the
`ros2_demo_workspace <https://github.com/renesas-rdk/ros2_demo_workspace>`_ repository fixes both
once, from the host: it stages the missing aarch64 libraries into ``~/app_temp`` and
``/opt/rcar-app-libs`` on the board, and symlinks ``/home/root`` to the home directory of the SSH
user.

.. code-block:: bash

   # Run these commands on the host machine
   wget https://raw.githubusercontent.com/renesas-rdk/ros2_demo_workspace/main/common_utils/setup_ubuntu_board_for_hyco.sh
   chmod +x setup_ubuntu_board_for_hyco.sh
   ./setup_ubuntu_board_for_hyco.sh <board IP address> ubuntu ubuntu

The arguments are the address, the SSH user and the password of the board; the last two default
to ``ubuntu``. The script needs ``sshpass`` on the host and a built
``reaction/tvm-app-linux-v4h2-cpu`` image, because the OpenCV libraries are taken out of it.

Run a Sample Common Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The evaluation flow of :doc:`reaction_usage` runs a model through the TVM RPC server, one
inference at a time. A common application is the other execution method: REACTION generates a
standalone C++ application for the model, copies it to the board and runs it there, which is what
product-level performance has to be measured with, because it can pipeline the work across
threads. The RPC server is not involved.

**Step 1 - Prepare the model folders**

Copy the model folders of the applications that are going to be run from the
``model-input-package-<ver>.tar.bz2`` add-on package into ``models`` in the REACTION root
directory, creating the directory if it does not exist. Each folder holds the files the
generator needs: ``prepostproc.cc``, the input QDQ model, ``CMakeLists.txt`` and
``exec_config.json``. The last two describe how the application is built and how it runs, see
:doc:`reaction_config`; the provided applications work as they are.

**Step 2 - Configure the experiment**

Only ``action: app`` is supported for common applications. Taking ``MobileNet_v1-app`` as the
example:

.. code-block:: yaml

   experiment:
     model_name: MobileNet_v1-app
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

The following applications are provided:

.. list-table:: Provided Common Applications
   :header-rows: 1
   :widths: 25 75

   * - Category
     - ``model_name``
   * - Classification
     - ``MobileNet_v1-app``, ``MobileNet_v2-app``, ``ResNet18-app``, ``ResNet50-app``,
       ``Swin-Tiny-app``
   * - Object detection
     - ``SSD-MobileNet_v1-app``, ``SSD-MobileNet_v2-app``, ``SSD-ResNet34-app``,
       ``YOLO_v5s-app``, ``YOLO_v5l-app``, ``YOLO_v7t-app``,
       ``RNet_OD_custom_node-app``, ``YOLO_v7t_custom_node-app``
   * - Semantic segmentation
     - ``HRNet_v2-app``, ``RNet_SS-app``
   * - Visualization on a monitor
     - ``Object_Detection_display-app``, ``Semantic_Segmentation_display-app``,
       ``Depth_Estimation_display-app``, ``OD_SS_display-app``
   * - Multiple models in parallel
     - ``MultiNets-app``
   * - Bird's Eye View
     - ``FastBEV-app``
   * - Multi-head
     - ``YOLOP-app``

.. note::

   ``remove_input_quantize`` and ``remove_output_dequantize`` must be ``true`` for the provided
   applications; both default to ``true``. ``ResNet50-app`` additionally needs
   ``skip_mean_quantization: true``, which is also the default for that case. The two
   ``custom_node`` applications need ``custom_node_config_path`` pointing at the matching file
   under ``configs/custom_node/``.

**Step 3 - Run the application**

.. code-block:: bash

   # Run this command from the activated environment, in the REACTION root directory
   reaction start

REACTION parses ``exec_config.json``, compiles the model into a ``.tar`` middleware, a ``.so``
library and an executable, prepares the input images, copies everything to the board and runs it
there with ``exec_config.json``. The performance metrics are printed at the end:

.. code-block:: text

   Total exec time (ms): 226.91
   Loop count: 400
   Throughput inv. (ms): 0.567274
   Throughput (fps): 1762.82

``Total exec time`` is the time spent on all images, ``Loop count`` the number of images
processed, ``Throughput inv.`` the average time per image and ``Throughput`` the number of
images per second.

To see the inference results as well, set ``print_inference: true`` in ``exec_config.json`` and
run the job again:

.. code-block:: text

   Thread (0) Top-1 prediction:  class_id = 282 , score = 0.764434
   Thread (1) Top-1 prediction:  class_id = 98 , score = 0.999645
   Total exec time (ms): 236.585
   Loop count: 400

.. important::

   With ``print_inference: true`` the metrics include the time spent printing or saving the
   results, so use a run with ``print_inference: false`` as the performance reference.

Where the results end up depends on what ``prepostproc.cc`` does: the console log is always
written, most of the object detection and segmentation applications and ``FastBEV-app`` also
write ``*.txt`` files in their application folder, and the visualization applications draw on
the monitor. Everything the run produced is kept under
``work_dir/<model_name>/tvm-<device>/common_application``, including the ``Log`` file with the
output of the board, the compiled ``models`` folder, the downloaded ``test_data`` and the relay
information files.

.. note::

   If ``keep_app_folder`` was set to ``true`` and data is still left in the output folder
   ``app_temp/`` on the board, the next ``reaction start`` fails with an error. Clear that
   folder before running again.

To run a model of your own as a common application, see :doc:`reaction_byom`.
