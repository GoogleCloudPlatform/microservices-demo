**To remove tags from a Data Store.**

The following ``untag-resource`` example shows how to remove tags from a Data Store. ::

    aws healthlake untag-resource \
        --resource-arn "arn:aws:healthlake:us-east-1:674914422125:datastore/fhir/b91723d65c6fdeb1d26543a49d2ed1fa" \
        --tag-keys '["key1"]' \
        --region us-east-1

This command produces no output.

For more information, see `Removing tags from a Data Store <https://docs.aws.amazon.com/healthlake/latest/devguide/remove-tags.html>`__ in the *Amazon HealthLake Developer Guide*.