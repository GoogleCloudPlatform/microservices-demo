**To list all FHIR import jobs**

The following ``list-fhir-import-jobs`` example shows how to use the command to view a list of all import jobs associated with an account. ::

    aws healthlake list-fhir-import-jobs \
        --datastore-id (Datastore ID) \
        --submitted-before (DATE like 2024-10-13T19:00:00Z) \
        --submitted-after (DATE like 2020-10-13T19:00:00Z ) \
        --job-name "FHIR-IMPORT" \
        --job-status SUBMITTED  \
        -max-results (Integer between 1 and 500)

Output::

    {
        "ImportJobProperties": {
            "OutputDataConfig": {
                "S3Uri": "s3://(Bucket Name)/(Prefix Name)/",
                    "S3Configuration": {
                        "S3Uri": "s3://(Bucket Name)/(Prefix Name)/",
                        "KmsKeyId" : "(KmsKey Id)"
        },
        },
            "DataAccessRoleArn": "arn:aws:iam::(AWS Account ID):role/(Role Name)",
            "JobStatus": "COMPLETED",
            "JobId": "c145fbb27b192af392f8ce6e7838e34f",
            "JobName" "FHIR-IMPORT",
            "SubmitTime": 1606272542.161,
            "EndTime": 1606272609.497,
            "DatastoreId": "(Datastore ID)"
        }
    }
    "NextToken": String

For more information, see `Importing files to FHIR Data Store <ttps://docs.aws.amazon.com/healthlake/latest/devguide/import-examples.html>`__ in the Amazon HealthLake Developer Guide.