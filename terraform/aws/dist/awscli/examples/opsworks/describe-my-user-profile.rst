**To obtain a user's profile**

The following example shows how to obtain the profile
of the AWS Identity and Access Management (IAM) user that is running the command. ::

  aws opsworks --region us-east-1 describe-my-user-profile

*Output*: For brevity, most of the user's SSH public key is replaced by an ellipsis (...). ::

  {
    "UserProfile": {
      "IamUserArn": "arn:aws:iam::123456789012:user/myusername", 
      "SshPublicKey": "ssh-rsa AAAAB3NzaC1yc2EAAAABJQ...3LQ4aX9jpxQw== rsa-key-20141104", 
      "Name": "myusername", 
      "SshUsername": "myusername"
    }
  }

**More Information**

For more information, see `Importing Users into AWS OpsWorks`_ in the *AWS OpsWorks User Guide*.

.. _`Importing Users into AWS OpsWorks`: http://docs.aws.amazon.com/opsworks/latest/userguide/opsworks-security-users-manage-import.html

