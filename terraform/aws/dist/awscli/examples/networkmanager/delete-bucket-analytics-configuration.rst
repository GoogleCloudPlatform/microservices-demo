**To delete an analytics configuration for a bucket**

The following ``delete-bucket-analytics-configuration`` example removes the analytics configuration for the specified bucket and ID. ::

    aws s3api delete-bucket-analytics-configuration \
        --bucket my-bucket \
        --id 1

This command produces no output.