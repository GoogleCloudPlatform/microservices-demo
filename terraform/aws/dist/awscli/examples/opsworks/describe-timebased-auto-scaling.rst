**To describe the time-based scaling configuration of an instance**

The following example describes a specified instance's time-based scaling configuration.
The instance is identified by its instance ID, which you can find on the instances's
details page or by running ``describe-instances``. ::

  aws opsworks describe-time-based-auto-scaling --region us-east-1 --instance-ids 701f2ffe-5d8e-4187-b140-77b75f55de8d

*Output*: The example has a single time-based instance. :: 

  {
    "TimeBasedAutoScalingConfigurations": [
     {
        "InstanceId": "701f2ffe-5d8e-4187-b140-77b75f55de8d", 
        "AutoScalingSchedule": {
          "Monday": {
            "11": "on", 
            "10": "on", 
            "13": "on", 
            "12": "on" 
          }, 
          "Tuesday": {
            "11": "on", 
            "10": "on", 
            "13": "on", 
            "12": "on" 
          } 
        }
      }
    ]
  }



**More Information**

For more information, see `How Automatic Time-based Scaling Works`_ in the *AWS OpsWorks User Guide*.

.. _`How Automatic Time-based Scaling Works`: http://docs.aws.amazon.com/opsworks/latest/userguide/workinginstances-autoscaling.html#workinginstances-autoscaling-timebased
