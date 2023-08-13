**To retrieve the request payment configuration for a bucket**

The following ``get-bucket-request-payment`` example retrieves the requester pays configuration for the specified bucket. ::

    aws s3api get-bucket-request-payment \
        --bucket my-bucket

Output::

    {
        "Payer": "BucketOwner"
    }
