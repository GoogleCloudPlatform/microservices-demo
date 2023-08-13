**To create a FHIR Data Store.**

The following ``create-fhir-datastore`` example demonstrates how to create a new Data Store in Amazon HealthLake. ::

    aws healthlake create-fhir-datastore \
        --region us-east-1 \
        --datastore-type-version R4 \
        --datastore-type-version R4 \
        --datastore-name "FhirTestDatastore"

Output::

    {
        "DatastoreEndpoint": "https://healthlake.us-east-1.amazonaws.com/datastore/(Datastore ID)/r4/",
        "DatastoreArn": "arn:aws:healthlake:us-east-1:(AWS Account ID):datastore/(Datastore ID)",
        "DatastoreStatus": "CREATING",
        "DatastoreId": "(Datastore ID)"
    }

For more information, see `Creating and monitoring a FHIR Data Store <https://docs.aws.amazon.com/healthlake/latest/devguide/working-with-FHIR-healthlake.html>`__ in the *Amazon HealthLake Developer Guide*.
