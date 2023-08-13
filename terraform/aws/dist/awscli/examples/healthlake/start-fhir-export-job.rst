**To start a FHIR export job**

The following ``start-fhir-export-job`` example shows how to start a FHIR export job using Amazon HealthLake. ::

    aws healthlake start-fhir-export-job \
        --output-data-config S3Uri="s3://(Bucket Name)/(Prefix Name)/" \
        --datastore-id (Datastore ID) \
        --data-access-role-arn arn:aws:iam::(AWS Account ID):role/(Role Name)

Output::

    {
        "DatastoreId": "(Datastore ID)",
        "JobStatus": "SUBMITTED",
        "JobId": "9b9a51943afaedd0a8c0c26c49135a31"
    }

For more information, see `Exporting files from a FHIR Data Store <https://docs.aws.amazon.com/healthlake/latest/devguide/export-datastore.html>`__ in the *Amazon HealthLake Developer Guide*.
