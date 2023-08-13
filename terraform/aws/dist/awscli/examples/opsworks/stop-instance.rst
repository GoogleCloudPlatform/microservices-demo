**To stop an instance**

The following example stops a specified instance, which is identified by its instance ID.
You can obtain an instance ID by going to the instance's details page on the AWS OpsWorks console or by
running the ``describe-instances`` command. ::

  aws opsworks stop-instance --region us-east-1 --instance-id 3a21cfac-4a1f-4ce2-a921-b2cfba6f7771

You can restart a stopped instance by calling ``start-instance`` or by deleting the instance by calling
``delete-instance``.

*Output*: None.

**More Information**

For more information, see `Stopping an Instance`_ in the *AWS OpsWorks User Guide*.

.. _`Stopping an Instance`: http://docs.aws.amazon.com/opsworks/latest/userguide/workinginstances-starting.html#workinginstances-starting-stop


