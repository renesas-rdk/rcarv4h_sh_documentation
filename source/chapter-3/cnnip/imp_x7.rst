What is IMP-X7?
^^^^^^^^^^^^^^^

IMP-X7 is the image recognition engine integrated in the Renesas R-Car V4H SoC used on the
R-Car V4H SH platform. It accelerates deep learning inference for computer vision workloads,
providing high-performance processing of image and video data for real-time analysis and
recognition.

The IMP-X7 consists of two accelerators: the CNN-IP (Convolutional Neural Network IP) and the
CEVA Vision DSP (4x SP500 DSP cores), both sharing a common scratchpad memory. Together with the
two application CPU clusters of the SoC (two Arm® Cortex®-A76 cores each), they handle complex
image recognition tasks efficiently.

.. figure:: ../../images/imp-x7.png
   :alt: IMP-X7 Block Diagram
   :width: 500px
   :align: center

   IMP-X7 Block Diagram

.. important::

   On the R-Car V4H SH platform, the CEVA Vision DSP **is not supported in this release**.
   Deep learning acceleration is therefore provided by the CNN-IP alone, with the
   Cortex-A76 application CPU clusters handling the remaining processing.

**Specifications**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Block
     - Specification
   * - CNN-IP
     - 29.5 TOPS (dense) convolution engine
   * - Scratchpad memory
     - 2.5 MB
   * - Application CPU
     - 2x Arm® Cortex®-A76 clusters, two cores each (4 cores total)
   * - CPU performance
     - Up to 40.3k DMIPS per cluster (80.6k DMIPS total)
