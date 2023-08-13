**To describe user profiles**

The following ``describe-user-profiles`` command describes the account's user profiles. ::

  aws opsworks --region us-east-1 describe-user-profiles

*Output*::

  {
    "UserProfiles": [
      {
        "IamUserArn": "arn:aws:iam::123456789012:user/someuser",
        "SshPublicKey": "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAkOuP7i80q3Cko...",
        "AllowSelfManagement": true,
        "Name": "someuser",
        "SshUsername": "someuser"
      },
      {
        "IamUserArn": "arn:aws:iam::123456789012:user/cli-user-test",
        "AllowSelfManagement": true,
        "Name": "cli-user-test",
        "SshUsername": "myusername"
      }
    ]
  }

**More Information**

For more information, see `Managing AWS OpsWorks Users`_ in the *AWS OpsWorks User Guide*.

.. _`Managing AWS OpsWorks Users`: http://docs.aws.amazon.com/opsworks/latest/userguide/opsworks-security-users-manage.html

