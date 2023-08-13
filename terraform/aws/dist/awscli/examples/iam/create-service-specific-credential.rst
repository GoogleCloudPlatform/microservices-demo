**Create a set of service-specific credentials for a user**

The following ``create-service-specific-credential`` example creates a username and password that can be used to access only the configured service. ::

    aws iam create-service-specific-credential --user-name sofia --service-name codecommit.amazonaws.com

Output::

  {
      "ServiceSpecificCredential": {
          "CreateDate": "2019-04-18T20:45:36+00:00",
          "ServiceName": "codecommit.amazonaws.com",
          "ServiceUserName": "sofia-at-123456789012",
          "ServicePassword": "k1zPZM6uVxMQ3oxqgoYlNuJPyRTZ1vREs76zTQE3eJk=",
          "ServiceSpecificCredentialId": "ACCAEXAMPLE123EXAMPLE",
          "UserName": "sofia",
          "Status": "Active"
      }
  }

For more information, see `Create Git Credentials for HTTPS Connections to CodeCommit`_ in the *AWS CodeCommit User Guide*

.. _`Create Git Credentials for HTTPS Connections to CodeCommit`: https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-gc.html#setting-up-gc-iam
