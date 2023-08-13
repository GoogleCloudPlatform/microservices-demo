**To retrieve the policy status for a bucket indicating whether the bucket is public**

The following ``get-bucket-policy-status`` example retrieves the policy status for the bucket ``my-bucket``. ::

    aws s3api get-bucket-policy-status \
        --bucket my-bucket

Output::

    {
        "PolicyStatus": {
            "IsPublic": false
        }
    }
