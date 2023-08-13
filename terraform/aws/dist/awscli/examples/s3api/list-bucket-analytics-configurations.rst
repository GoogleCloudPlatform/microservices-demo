**To retrieve a list of analytics configurations for a bucket**

The following ``list-bucket-analytics-configurations`` retrieves a list of analytics configurations for the specified bucket. ::

    aws s3api list-bucket-analytics-configurations \
        --bucket my-bucket

Output::

    {
        "AnalyticsConfigurationList": [
            {
                "StorageClassAnalysis": {},
                "Id": "1"
            }
        ],
        "IsTruncated": false
    }
