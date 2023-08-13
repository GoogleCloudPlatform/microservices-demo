**To delete a server certificate from your AWS account**

The following ``delete-server-certificate`` command removes the specified server certificate from your AWS account. This command produces no output. ::

    aws iam delete-server-certificate --server-certificate-name myUpdatedServerCertificate

To list the server certificates available in your AWS account, use the ``list-server-certificates`` command.

For more information, see `Creating, Uploading, and Deleting Server Certificates`_ in the *IAM Users Guide*.

.. _`Creating, Uploading, and Deleting Server Certificates`: http://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_server-certs.html
