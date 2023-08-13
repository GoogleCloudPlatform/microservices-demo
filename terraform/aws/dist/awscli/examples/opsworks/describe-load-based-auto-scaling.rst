**To describe a layer's load-based scaling configuration**

The following example describes a specified layer's load-based scaling configuration.
The layer is identified by its layer ID, which you can find on the layer's
details page or by running ``describe-layers``. ::

  aws opsworks describe-load-based-auto-scaling --region us-east-1 --layer-ids 6bec29c9-c866-41a0-aba5-fa3e374ce2a1

*Output*: The example layer has a single load-based instance. :: 

  {
    "LoadBasedAutoScalingConfigurations": [
      {
        "DownScaling": {
          "IgnoreMetricsTime": 10, 
          "ThresholdsWaitTime": 10, 
          "InstanceCount": 1, 
          "CpuThreshold": 30.0
        }, 
        "Enable": true, 
        "UpScaling": {
          "IgnoreMetricsTime": 5, 
          "ThresholdsWaitTime": 5, 
          "InstanceCount": 1, 
          "CpuThreshold": 80.0
        }, 
        "LayerId": "6bec29c9-c866-41a0-aba5-fa3e374ce2a1"
      }
    ]
  }


**More Information**

For more information, see `How Automatic Load-based Scaling Works`_ in the *AWS OpsWorks User Guide*.

.. _`How Automatic Load-based Scaling Works`: http://docs.aws.amazon.com/opsworks/latest/userguide/workinginstances-autoscaling.html#workinginstances-autoscaling-loadbased
