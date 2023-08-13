**To describe a FHIR export job**

The following ``describe-fhir-export-job`` example shows how to find the properties of a FHIR export job in Amazon HealthLake. ::

    aws healthlake describe-fhir-export-job \
        --datastore-id (Datastore ID) \
        --job-id 9b9a51943afaedd0a8c0c26c49135a31

Output::

    {
        "ExportJobProperties": {
            "DataAccessRoleArn": "arn:aws:iam::(AWS Account ID):role/(Role Name)",
            "JobStatus": "IN_PROGRESS",
            "JobId": "9009813e9d69ba7cf79bcb3468780f16",
            "SubmitTime": 1609175692.715,
            "OutputDataConfig": {
                "S3Uri": "s3://(Bucket Name)/(Prefix Name)/59593b2d0367ce252b5e66bf5fd6b574-FHIR_EXPORT-9009813e9d69ba7cf79bcb3468780f16/"
            },
            "DatastoreId": "(Datastore ID)"
        }
    }

For more information, see `Exporting files from a FHIR Data Store <https://docs.aws.amazon.com/healthlake/latest/devguide/export-datastore.html>`__ in the *Amazon HealthLake Developer Guide*.
