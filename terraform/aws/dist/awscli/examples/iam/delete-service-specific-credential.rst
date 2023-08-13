**Delete a service-specific credential for the requesting user**

The following ``delete-service-specific-credential`` example deletes the specified service-specific credential for the user making the request. The ``service-specific-credential-id`` is provided when you create the credential and you can retrieve it by using the ``list-service-specific-credentials`` command. This command produces no output. ::

    aws iam delete-service-specific-credential --service-specific-credential-id ACCAEXAMPLE123EXAMPLE

**Delete a service-specific credential for a specified user**

The following ``delete-service-specific-credential`` example deletes the specified service-specific credential for the specified user. The ``service-specific-credential-id`` is provided when you create the credential and you can retrieve it by using the ``list-service-specific-credentials`` command. This command produces no output. ::

    aws iam delete-service-specific-credential --user-name sofia --service-specific-credential-id ACCAEXAMPLE123EXAMPLE

For more information, see `Create Git Credentials for HTTPS Connections to CodeCommit`_ in the *AWS CodeCommit User Guide*

.. _`Create Git Credentials for HTTPS Connections to CodeCommit`: https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-gc.html#setting-up-gc-iam
