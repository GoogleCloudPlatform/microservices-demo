**To describe a stack's configuration**

The following ``describe-stack-summary`` command returns a summary of the specified stack's configuration. ::

  aws opsworks --region us-east-1 describe-stack-summary --stack-id 8c428b08-a1a1-46ce-a5f8-feddc43771b8

*Output*::

  {
    "StackSummary": {
      "StackId": "8c428b08-a1a1-46ce-a5f8-feddc43771b8",
      "InstancesCount": {
        "Booting": 1
      },
      "Name": "CLITest",
      "AppsCount": 1,
      "LayersCount": 1,
      "Arn": "arn:aws:opsworks:us-west-2:123456789012:stack/8c428b08-a1a1-46ce-a5f8-feddc43771b8/"
    }
  }

**More Information**

For more information, see `Stacks`_ in the *AWS OpsWorks User Guide*.

.. _`Stacks`: http://docs.aws.amazon.com/opsworks/latest/userguide/workingstacks.html

