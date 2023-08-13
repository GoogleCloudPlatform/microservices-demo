**To sets an analytics configuration for the bucket**

The following ``put-bucket-analytics-configuration`` example configures analytics for the specified bucket. ::

    aws s3api put-bucket-analytics-configuration \
        --bucket my-bucket --id 1 \
        --analytics-configuration '{"Id": "1","StorageClassAnalysis": {}}'

This command produces no output.
