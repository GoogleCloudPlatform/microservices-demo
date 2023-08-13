**To list the signing certificates for an IAM user**

The following ``list-signing-certificates`` command lists the signing certificates for the IAM user named ``Bob``. ::

    aws iam list-signing-certificates \
        --user-name Bob

Output::

    {
        "Certificates": [
            {
                "UserName": "Bob",
                "Status": "Inactive",
                "CertificateBody": "-----BEGIN CERTIFICATE-----<certificate-body>-----END CERTIFICATE-----",
                "CertificateId": "TA7SMP42TDN5Z26OBPJE7EXAMPLE",
                "UploadDate": "2013-06-06T21:40:08Z"
            }
        ]
    }

For more information, see `Creating and Uploading a User Signing Certificate <https://docs.aws.amazon.com/IAM/latest/UserGuide/Using_UploadCertificate.html>`__ in the *Using IAM* guide.