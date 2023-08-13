**To retrieve the object retention configuration for an object**

The following ``get-object-retention`` example retrieves the object retention configuration for the specified object. ::

    aws s3api get-object-retention \
        --bucket my-bucket-with-object-lock \
        --key doc1.rtf

Output::

    {
        "Retention": {
            "Mode": "GOVERNANCE",
            "RetainUntilDate": "2025-01-01T00:00:00.000Z"
        }
    }
