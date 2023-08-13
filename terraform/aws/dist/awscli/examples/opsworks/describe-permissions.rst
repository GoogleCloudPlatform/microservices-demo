**To obtain a user's per-stack AWS OpsWorks permission level**

The following example shows how to to obtain an AWS Identity and Access Management (IAM) user's permission level on a specified stack. ::

  aws opsworks --region us-east-1 describe-permissions --iam-user-arn arn:aws:iam::123456789012:user/cli-user-test --stack-id d72553d4-8727-448c-9b00-f024f0ba1b06

*Output*::

  {
    "Permissions": [
      {
        "StackId": "d72553d4-8727-448c-9b00-f024f0ba1b06", 
        "IamUserArn": "arn:aws:iam::123456789012:user/cli-user-test", 
        "Level": "manage", 
        "AllowSudo": true, 
        "AllowSsh": true
      }
    ]
  }


**More Information**

For more information, see `Granting Per-Stack Permissions Levels`_ in the *AWS OpsWorks User Guide*.

.. _`Granting Per-Stack Permissions Levels`: http://docs.aws.amazon.com/opsworks/latest/userguide/opsworks-security-users-console.html
