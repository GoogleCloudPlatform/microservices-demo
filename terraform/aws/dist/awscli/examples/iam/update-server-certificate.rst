**To change the path or name of a server certificate in your AWS account**

The following ``update-server-certificate`` command changes the name of the certificate from ``myServerCertificate`` to ``myUpdatedServerCertificate``. It also changes the path to ``/cloudfront/`` so that it can be accessed by the Amazon CloudFront service. This command produces no output. You can see the results of the update by running the ``list-server-certificates`` command. ::

    aws-iam update-server-certificate --server-certificate-name myServerCertificate --new-server-certificate-name myUpdatedServerCertificate --new-path /cloudfront/

For more information, see `Creating, Uploading, and Deleting Server Certificates`_ in the *IAM Users Guide*.

.. _`Creating, Uploading, and Deleting Server Certificates`: http://docs.aws.amazon.com/IAM/latest/UserGuide/InstallCert.html
