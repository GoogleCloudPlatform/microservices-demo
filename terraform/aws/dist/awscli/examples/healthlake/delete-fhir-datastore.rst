**To delete a FHIR Data Store**

The following ``delete-fhir-datastore`` example demonstrates how to delete a Data Store and all of its contents in Amazon HealthLake. ::

    aws healthlake delete-fhir-datastore \
        --datastore-id (Data Store ID) \
        --region us-east-1

Output::

    {
        "DatastoreEndpoint": "https://healthlake.us-east-1.amazonaws.com/datastore/(Datastore ID)/r4/",
        "DatastoreArn": "arn:aws:healthlake:us-east-1:(AWS Account ID):datastore/(Datastore ID)",
        "DatastoreStatus": "DELETING",
        "DatastoreId": "(Datastore ID)"
    }

For more information, see `Creating and monitoring a FHIR Data Store <https://docs.aws.amazon.com/healthlake/latest/devguide/working-with-FHIR-healthlake.html>` in the *Amazon HealthLake Developer Guide*.
