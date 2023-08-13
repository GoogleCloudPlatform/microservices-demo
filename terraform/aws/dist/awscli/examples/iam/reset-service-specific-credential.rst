**Reset the password for a service-specific credential attached to the user making the request**

The following ``reset-service-specific-credential`` example generates a new cryptographically strong password for the specified service-specific credential attached to the user making the request. ::

    aws iam reset-service-specific-credential --service-specific-credential-id ACCAEXAMPLE123EXAMPLE
    
Output::

  {
      "ServiceSpecificCredential": {
          "CreateDate": "2019-04-18T20:45:36+00:00",
          "ServiceName": "codecommit.amazonaws.com",
          "ServiceUserName": "sofia-at-123456789012",
          "ServicePassword": "+oaFsNk7tLco+C/obP9GhhcOzGcKOayTmE3LnAmAmH4=",
          "ServiceSpecificCredentialId": "ACCAEXAMPLE123EXAMPLE",
          "UserName": "sofia",
          "Status": "Active"
      }
  }

**Reset the password for a service-specific credential attached to a specified user**

The following ``reset-service-specific-credential`` example generates a new cryptographically strong password for a service-specific credential attached to the specified user. ::

    aws iam reset-service-specific-credential --user-name sofia --service-specific-credential-id ACCAEXAMPLE123EXAMPLE
    
Output::

  {
      "ServiceSpecificCredential": {
          "CreateDate": "2019-04-18T20:45:36+00:00",
          "ServiceName": "codecommit.amazonaws.com",
          "ServiceUserName": "sofia-at-123456789012",
          "ServicePassword": "+oaFsNk7tLco+C/obP9GhhcOzGcKOayTmE3LnAmAmH4=",
          "ServiceSpecificCredentialId": "ACCAEXAMPLE123EXAMPLE",
          "UserName": "sofia",
          "Status": "Active"
      }
  }

For more information, see `Create Git Credentials for HTTPS Connections to CodeCommit`_ in the *AWS CodeCommit User Guide*

.. _`Create Git Credentials for HTTPS Connections to CodeCommit`: https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-gc.html#setting-up-gc-iam
