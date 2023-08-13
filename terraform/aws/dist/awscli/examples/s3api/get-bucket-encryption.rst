**To retrieve the server-side encryption configuration for a bucket**

The following ``get-bucket-encryption`` example retrieves the server-side encryption configuration for the bucket ``my-bucket``. ::

    aws s3api get-bucket-encryption \
        --bucket my-bucket

Output::

    {
        "ServerSideEncryptionConfiguration": {
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }
            ]
        }
    }
