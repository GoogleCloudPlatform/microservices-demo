**To add a tag to Data Store**

The following ``tag-resource`` example shows how to add a tag to a Data Store. ::

    aws healthlake tag-resource \
        --resource-arn "arn:aws:healthlake:us-east-1:691207106566:datastore/fhir/0725c83f4307f263e16fd56b6d8ebdbe" \
        --tags '[{"Key": "key1", "Value": "value1"}]' \
        --region us-east-1

This command produces no output.

For more information, see 'Adding a tag to a Data Store <https://docs.aws.amazon.com/healthlake/latest/devguide/add-a-tag.html>'__ in the *Amazon HealthLake Developer Guide.*.