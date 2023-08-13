**To update the password for an IAM user**

The following ``update-login-profile`` command creates a new password for the IAM user named ``Bob``::

  aws iam update-login-profile --user-name Bob --password <password>

To set a password policy for the account, use the ``update-account-password-policy`` command. If the new password
violates the account password policy, the command returns a ``PasswordPolicyViolation`` error.

If the account password policy allows them to, IAM users can change their own passwords using the ``change-password`` command.

Store the password in a secure place. If the password is lost, it cannot be recovered, and you must create a new one using the ``create-login-profile`` command.

For more information, see `Managing Passwords`_ in the *Using IAM* guide.

.. _`Managing Passwords`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_ManagingLogins.html


