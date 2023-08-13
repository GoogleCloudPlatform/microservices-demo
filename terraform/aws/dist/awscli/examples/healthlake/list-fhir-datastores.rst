**To list FHIR Data Stores**

The following ``list-fhir-datastores`` example shows to how to use the command and how users can filter results based on Data Store status in Amazon HealthLake. ::

    aws healthlake list-fhir-datastores \
        --region us-east-1 \
        --filter DatastoreStatus=ACTIVE

Output::

    {
        "DatastorePropertiesList": [
        {
            "PreloadDataConfig": {
                "PreloadDataType": "SYNTHEA"
            },
            "DatastoreName": "FhirTestDatastore",
            "DatastoreArn": "arn:aws:healthlake:us-east-1:<AWS Account ID>:datastore/<Datastore ID>",
            "DatastoreEndpoint": "https://healthlake.us-east-1.amazonaws.com/datastore/<Datastore ID>/r4/",
            "DatastoreStatus": "ACTIVE",
            "DatastoreTypeVersion": "R4",
            "CreatedAt": 1605574003.209,
            "DatastoreId": "<Datastore ID>"
        },
        {
            "DatastoreName": "Demo",
            "DatastoreArn": "arn:aws:healthlake:us-east-1:<AWS Account ID>:datastore/<Datastore ID>",
            "DatastoreEndpoint": "https://healthlake.us-east-1.amazonaws.com/datastore/<Datastore ID>/r4/",
            "DatastoreStatus": "ACTIVE",
            "DatastoreTypeVersion": "R4",
            "CreatedAt": 1603761064.881,
            "DatastoreId": "<Datastore ID>"
        }
        ]
    }

For more information, see `Creating and monitoring a FHIR Data Store <https://docs.aws.amazon.com/healthlake/latest/devguide/working-with-FHIR-healthlake.html>`__ in the *Amazon HealthLake Developer Guide*.
