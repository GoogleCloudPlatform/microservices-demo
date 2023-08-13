**To create a publishing destination to export GuardDuty findings in the current region to.**

This example shows how to create a publishing destination for GuardDuty findings. ::

    aws guardduty create-publishing-destination \
        --detector-id b6b992d6d2f48e64bc59180bfexample \
        --destination-type S3 \
        --destination-properties DestinationArn=arn:aws:s3:::yourbucket,KmsKeyArn=arn:aws:kms:us-west-1:111122223333:key/84cee9c5-dea1-401a-ab6d-e1de7example

Output::

    {
        "DestinationId": "46b99823849e1bbc242dfbe3cexample"
    }

For more information, see `Exporting findings <https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_exportfindings.html>`__ in the *GuardDuty User Guide*.