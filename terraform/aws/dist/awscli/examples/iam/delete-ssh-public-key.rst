**To delete an SSH public keys attached to an IAM user**

The following ``delete-ssh-public-key`` command deletes the specified SSH public key attached to the IAM user ``sofia``. This command does not produce any output. ::

    aws iam delete-ssh-public-key --user-name sofia --ssh-public-key-id APKA123456789EXAMPLE

For more information about SSH keys in IAM, see `Use SSH Keys and SSH with CodeCommit <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_ssh-keys.html#ssh-keys-code-commit>`_ in the *AWS IAM User Guide*.
