**To start a FHIR import job**

The following ``start-fhir-import-job`` example shows how to start a FHIR import job using Amazon HealthLake. ::

    aws healthlake start-fhir-import-job \
        --input-data-config S3Uri="s3://(Bucket Name)/(Prefix Name)/" \
        --datastore-id (Datastore ID) \
        --data-access-role-arn "arn:aws:iam::(AWS Account ID):role/(Role Name)" \
        --region us-east-1

Output::

    {
        "DatastoreId": "(Datastore ID)",
        "JobStatus": "SUBMITTED",
        "JobId": "c145fbb27b192af392f8ce6e7838e34f"
    }

For more information, see `Importing files to a FHIR Data Store 'https://docs.aws.amazon.com/healthlake/latest/devguide/import-datastore.html`__ in the *Amazon HeatlhLake Developer Guide*.
