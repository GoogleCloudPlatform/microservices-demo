**To create a user profile**

You import an AWS Identity and Access Manager (IAM) user into AWS OpsWorks by calling `create-user-profile` to create a user profile.
The following example creates a user profile for the cli-user-test IAM user, who
is identified by Amazon Resource Name (ARN). The example assigns the user an SSH username of ``myusername`` and enables self management,
which allows the user to specify an SSH public key. ::

  aws opsworks --region us-east-1 create-user-profile --iam-user-arn arn:aws:iam::123456789102:user/cli-user-test --ssh-username myusername --allow-self-management

*Output*::

  {
    "IamUserArn": "arn:aws:iam::123456789102:user/cli-user-test"
  }

**Tip**: This command imports an IAM user into AWS OpsWorks, but only with the permissions that are
granted by the attached policies. You can grant per-stack AWS OpsWorks permissions by using the ``set-permissions`` command.

**More Information**

For more information, see `Importing Users into AWS OpsWorks`_ in the *AWS OpsWorks User Guide*.

.. _`Importing Users into AWS OpsWorks`: http://docs.aws.amazon.com/opsworks/latest/userguide/opsworks-security-users-manage-import.html

