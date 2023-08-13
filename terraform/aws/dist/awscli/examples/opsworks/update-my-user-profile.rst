**To update a user's profile**

The following example updates the ``development`` user's profile to use a specified SSH public key.
The user's AWS credentials are represented by the ``development`` profile in the ``credentials`` file
(``~\.aws\credentials``), and the key is in a ``.pem`` file in the working directory. ::

  aws opsworks --region us-east-1 --profile development update-my-user-profile --ssh-public-key file://development_key.pem

*Output*: None.

**More Information**

For more information, see `Editing AWS OpsWorks User Settings`_ in the *AWS OpsWorks User Guide*.

.. _`Editing AWS OpsWorks User Settings`: http://docs.aws.amazon.com/opsworks/latest/userguide/opsworks-security-users-manage-edit.html

