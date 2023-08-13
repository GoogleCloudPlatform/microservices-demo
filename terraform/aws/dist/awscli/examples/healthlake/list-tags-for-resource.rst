**To list tags for a Data Store**

The following ``list-tags-for-resource`` example lists the tags associated with the specified Data Store.::

    aws healthlake list-tags-for-resource \
        --resource-arn "arn:aws:healthlake:us-east-1:674914422125:datastore/fhir/0725c83f4307f263e16fd56b6d8ebdbe" \
        --region us-east-1

Output::

    {
        "tags": {
            "key": "value",
            "key1": "value1"
        }
    }

For more information, see `Tagging resources in Amazon HealthLake <https://docs.aws.amazon.com/healthlake/latest/devguide/tagging.html>`__ in the Amazon HealthLake Developer Guide.