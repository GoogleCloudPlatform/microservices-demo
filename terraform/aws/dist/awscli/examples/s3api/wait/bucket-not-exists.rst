**To wait (pause running) until a bucket no longer exists**

The following ``wait bucket-not-exists`` example pauses and continues only after it can confirm that the specified bucket doesn't exist. ::

    aws s3api wait bucket-not-exists \
        --bucket my-bucket

This command produces no output.
