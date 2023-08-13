**To delete a user profile and remove an IAM user from AWS OpsWorks**

The following example deletes the user profile for a specified AWS Identity and Access Management
(IAM) user, who
is identified by Amazon Resource Name (ARN). The operation removes the user from AWS OpsWorks, but
does not delete the IAM user. You must use the IAM console, CLI, or API for that task. ::

  aws opsworks --region us-east-1 delete-user-profile --iam-user-arn arn:aws:iam::123456789102:user/cli-user-test

*Output*: None.

**More Information**

For more information, see `Importing Users into AWS OpsWorks`_ in the *AWS OpsWorks User Guide*.

.. _`Importing Users into AWS OpsWorks`: http://docs.aws.amazon.com/opsworks/latest/userguide/opsworks-security-users-manage-import.html

