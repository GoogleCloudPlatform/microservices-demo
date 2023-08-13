**To see the current account password policy**

The following ``get-account-password-policy`` command displays details about the password policy for the current account::

    aws iam get-account-password-policy

Output::

  {
      "PasswordPolicy": {
          "AllowUsersToChangePassword": false,
          "RequireLowercaseCharacters": false,
          "RequireUppercaseCharacters": false,
          "MinimumPasswordLength": 8,
          "RequireNumbers": true,
          "RequireSymbols": true
      }
  }

If no password policy is defined for the account, the command returns a ``NoSuchEntity`` error.

For more information, see `Managing an IAM Password Policy`_ in the *Using IAM* guide.

.. _`Managing an IAM Password Policy`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_ManagingPasswordPolicies.html
