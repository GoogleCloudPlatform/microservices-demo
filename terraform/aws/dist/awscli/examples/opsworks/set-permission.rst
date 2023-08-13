**To grant per-stack AWS OpsWorks permission levels**

When you import an AWS Identity and Access Management (IAM) user into AWS OpsWorks by calling ``create-user-profile``, the user has only those
permissions that are granted by the attached IAM policies.
You can grant AWS OpsWorks permissions by modifying a user's policies.
However, it is often easier to import a user and then use the ``set-permission`` command to grant
the user one of the standard permission levels for each stack to which the user will need access.

The following example grants permission for the specified stack for a user, who
is identified by Amazon Resource Name (ARN). The example grants the user a Manage permissions level, with sudo and SSH privileges on the stack's
instances. ::

  aws opsworks set-permission --region us-east-1 --stack-id 71c7ca72-55ae-4b6a-8ee1-a8dcded3fa0f --level manage  --iam-user-arn arn:aws:iam::123456789102:user/cli-user-test --allow-ssh --allow-sudo
  

*Output*: None.

**More Information**

For more information, see `Granting AWS OpsWorks Users Per-Stack Permissions`_ in the *AWS OpsWorks User Guide*.

.. _`Granting AWS OpsWorks Users Per-Stack Permissions`: http://docs.aws.amazon.com/opsworks/latest/userguide/opsworks-security-users-console.html

