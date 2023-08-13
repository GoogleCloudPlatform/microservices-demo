**To retrieve the logging status for a bucket**

The following ``get-bucket-logging`` example retrieves the logging status for the specified bucket. ::

    aws s3api get-bucket-logging \
        --bucket my-bucket

Output::

    {
        "LoggingEnabled": {
            "TargetPrefix": "",
            "TargetBucket": "my-bucket-logs"
              }
    }
