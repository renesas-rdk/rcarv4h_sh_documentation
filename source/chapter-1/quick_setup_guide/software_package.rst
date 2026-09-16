.. _sh_software_package:

Downloading the software package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Everything you need to bring up the board is distributed in a single software package: the
``ipl-burning`` script that writes the Initial Program Loader to the board, and the Ubuntu 24.04
Server image that you flash onto the microSD card. Download the package to your host PC before
you start:

`R-Car V4H Sparrow Hawk Software package <https://github.com/renesas-rdk/rcarv4h_sh_documentation/releases>`_

Extract the ``r-car-v4h-sparrow-hawk-software-package-v***.zip`` file. The ``board_setup`` folder inside it has the following structure:

.. code-block:: text

   board_setup/
   ├── board_image/
   │   ├── ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.xz
   │   └── ubuntu-24.04-server-arm64-rcarv4h-sparrowhawk.img.bmap
   └── ipl-burning/
       ├── run.sh
       ├── run.bat
       └── ...

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - **Folder**
     - **Description**
   * - ``board_image/``
     - Ubuntu 24.04 Server microSD card image and its block map file.

       Used in :ref:`Preparing the root file system microSD card <sh_prepare_microsd>`.
   * - ``ipl-burning/``
     - Script that writes the Initial Program Loader to the board's serial flash ROM.

       Used in :ref:`Flashing the IPL <flashing_the_ipl>`.

The next sections of this guide assume that you have already downloaded and extracted the software package to your host PC.
