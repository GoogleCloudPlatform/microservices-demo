**To set the load-based scaling configuration for a layer**

The following example enables load-based scaling for a specified layer and sets the configuration
for that layer.
You must use ``create-instance`` to add load-based instances to the layer. ::

  aws opsworks --region us-east-1 set-load-based-auto-scaling --layer-id 523569ae-2faf-47ac-b39e-f4c4b381f36d --enable --up-scaling file://upscale.json --down-scaling file://downscale.json

The example puts the upscaling threshold settings in a separate file in the working directory named ``upscale.json``, which contains the following. ::

  {
    "InstanceCount": 2,
    "ThresholdsWaitTime": 3,
    "IgnoreMetricsTime": 3,
    "CpuThreshold": 85,
    "MemoryThreshold": 85,
    "LoadThreshold": 85
  }
  
The example puts the downscaling threshold settings in a separate file in the working directory named ``downscale.json``, which contains the following. ::

  {
  "InstanceCount": 2,
  "ThresholdsWaitTime": 3,
  "IgnoreMetricsTime": 3,
  "CpuThreshold": 35,
  "MemoryThreshold": 30,
  "LoadThreshold": 30
  }

*Output*: None.

**More Information**

For more information, see `Using Automatic Load-based Scaling`_ in the *AWS OpsWorks User Guide*.

.. _`Using Automatic Load-based Scaling`: http://docs.aws.amazon.com/opsworks/latest/userguide/workinginstances-autoscaling-loadbased.html

