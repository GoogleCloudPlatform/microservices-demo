**To describe certificates**

The following ``describe-certificates`` example retrieves the details of the certificate associated with the user's default region. ::

    aws rds describe-certificates

Output::

    {
        "Certificates": [
            {
                "Thumbprint": "34478a908a83ae45dcb61676d235ece975c62c63",
                "ValidFrom": "2015-02-05T21:54:04Z",
                "CertificateIdentifier": "rds-ca-2015",
                "ValidTill": "2020-03-05T21:54:04Z",
                "CertificateType": "CA",
                "CertificateArn": "arn:aws:rds:us-east-1::cert:rds-ca-2015"
            }
        ]
    }
