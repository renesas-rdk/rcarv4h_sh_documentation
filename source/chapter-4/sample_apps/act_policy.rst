.. _act_policy_support:

Action Chunking Transformer (ACT) Policy Support
------------------------------------------------

Beyond the sample applications listed in :ref:`Sample Applications <sample_apps>`, the R-Car V4H SH
also runs Action Chunking Transformer (ACT), a Vision-Language-Action policy for
imitation-learning based manipulation. The policy takes camera images and the current robot state
and predicts a chunk of future actions, which the robot executes directly. It is compiled for the
CNN-IP with the same REACTION toolchain used for every model in the
:ref:`Model Zoo <model_zoo>`, and it runs on the board in real time.

ACT is not part of the public Model Zoo, and no sample application in this chapter uses it. The
policy weights, the model configuration, the training data recipe, and the integration code are
not published with this documentation.

.. note::

   If you want to evaluate or deploy an ACT policy on the R-Car V4H SH, get in touch so we can
   discuss your use case directly. Open an issue on
   `renesas-rdk <https://github.com/renesas-rdk/rcarv4h_sh_documentation>`_ or contact your
   Renesas representative. Please do not expect implementation details in this documentation.
