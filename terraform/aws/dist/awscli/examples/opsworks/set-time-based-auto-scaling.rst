**To set the time-based scaling configuration for a layer**

The following example sets the time-based configuration for a specified instance.
You must first use ``create-instance`` to add the instance to the layer. ::

  aws opsworks --region us-east-1 set-time-based-auto-scaling --instance-id 69b6237c-08c0-4edb-a6af-78f3d01cedf2 --auto-scaling-schedule file://schedule.json

The example puts the schedule in a separate file in the working directory named ``schedule.json``.
For this example, the instance is on for a few hours around midday UTC (Coordinated Universal Time) on Monday and Tuesday. ::

  {
    "Monday": {
      "10": "on",
      "11": "on",
      "12": "on",
      "13": "on"
    }, 
    "Tuesday": {
      "10": "on",
      "11": "on",
      "12": "on",
      "13": "on" 
    }
  }

*Output*: None.

**More Information**

For more information, see `Using Automatic Time-based Scaling`_ in the *AWS OpsWorks User Guide*.

.. _`Using Automatic Time-based Scaling`: http://docs.aws.amazon.com/opsworks/latest/userguide/workinginstances-autoscaling-timebased.html

