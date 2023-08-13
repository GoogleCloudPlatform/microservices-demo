**To update your Multi-Region Access Point routing configuration**

The following ``submit-multi-region-access-point-routes`` example updates the routing statuses of ``DOC-EXAMPLE-BUCKET-1`` and ``DOC-EXAMPLE-BUCKET-2`` in the ``ap-southeast-2`` Region for your Multi-Region Access Point. ::

    aws s3control submit-multi-region-access-point-routes \
        --region ap-southeast-2 \
        --account-id 111122223333 \
        --mrap MultiRegionAccessPoint_ARN \
        --route-updates Bucket=DOC-EXAMPLE-BUCKET-1,TrafficDialPercentage=100 Bucket=DOC-EXAMPLE-BUCKET-2,TrafficDialPercentage=0

This command produces no output.