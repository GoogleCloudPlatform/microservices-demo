**To create a stack**

The following ``create-stack`` command creates a stack named CLI Stack. ::

  aws opsworks create-stack --name "CLI Stack" --stack-region "us-east-1" --service-role-arn arn:aws:iam::123456789012:role/aws-opsworks-service-role --default-instance-profile-arn arn:aws:iam::123456789012:instance-profile/aws-opsworks-ec2-role --region us-east-1

The ``service-role-arn`` and ``default-instance-profile-arn`` parameters are required. You typically
use the ones that AWS OpsWorks
creates for you when you create your first stack. To get the Amazon Resource Names (ARNs) for your
account, go to the `IAM console`_, choose ``Roles`` in the navigation panel,
choose the role or profile, and choose the ``Summary`` tab.

.. _`IAM console`: https://console.aws.amazon.com/iam/home

*Output*::

  {
    "StackId": "f6673d70-32e6-4425-8999-265dd002fec7"
  }

**More Information**

For more information, see `Create a New Stack`_ in the *AWS OpsWorks User Guide*.

.. _`Create a New Stack`: http://docs.aws.amazon.com/opsworks/latest/userguide/workingstacks-creating.html
