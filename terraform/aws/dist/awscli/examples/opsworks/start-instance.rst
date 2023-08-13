**To start an instance**

The following ``start-instance`` command starts a specified 24/7 instance. ::

  aws opsworks start-instance --instance-id f705ee48-9000-4890-8bd3-20eb05825aaf

*Output*: None. Use describe-instances_ to check the instance's status.

.. _describe-instances: http://docs.aws.amazon.com/cli/latest/reference/opsworks/describe-instances.html

**Tip** You can start every offline instance in a stack with one command by calling start-stack_.

.. _start-stack: http://docs.aws.amazon.com/cli/latest/reference/opsworks/start-stack.html

**More Information**

For more information, see `Manually Starting, Stopping, and Rebooting 24/7 Instances`_ in the *AWS OpsWorks User Guide*.

.. _`Manually Starting, Stopping, and Rebooting 24/7 Instances`: http://docs.aws.amazon.com/opsworks/latest/userguide/workinginstances-starting.html

