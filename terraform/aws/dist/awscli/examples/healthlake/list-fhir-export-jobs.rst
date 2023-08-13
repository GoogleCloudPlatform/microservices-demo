**To list all FHIR export jobs**

The following ``list-fhir-export-jobs`` example shows how to use the command to view a list of export jobs associated with an account. ::

    aws healthlake list-fhir-export-jobs \
        --datastore-id (Datastore ID) \
        --submitted-before (DATE like 2024-10-13T19:00:00Z)\
        --submitted-after (DATE like 2020-10-13T19:00:00Z )\
        --job-name "FHIR-EXPORT" \
        --job-status SUBMITTED  \
        --max-results (Integer between 1 and 500)

Output::

    {
        "ExportJobProperties": {
            "OutputDataConfig": {
                "S3Uri": "s3://(Bucket Name)/(Prefix Name)/"
                    "S3Configuration": {
                    "S3Uri": "s3://(Bucket Name)/(Prefix Name)/",
                    "KmsKeyId" : "(KmsKey Id)"
            },
        },
        "DataAccessRoleArn": "arn:aws:iam::(AWS Account ID):role/(Role Name)",
        "JobStatus": "COMPLETED",
        "JobId": "c145fbb27b192af392f8ce6e7838e34f",
        "JobName" "FHIR-EXPORT",
        "SubmitTime": 1606272542.161,
        "EndTime": 1606272609.497,
        "DatastoreId": "(Datastore ID)"
        }
    }
    "NextToken": String

For more information, see `Exporting files from a FHIR Data Store <https://docs.aws.amazon.com/healthlake/latest/devguide/export-datastore.html>`__ in the Amazon HealthLake Developer Guide.