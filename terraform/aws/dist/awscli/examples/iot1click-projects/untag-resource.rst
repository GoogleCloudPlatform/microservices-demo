**To remove tags from a project resource**

The following ``untag-resource`` example removes the tag with the key name ``Manager`` from the specified project. ::

    aws iot1click-projects untag-resource \
        --resource-arn "arn:aws:iot1click:us-west-2:123456789012:projects/AnytownDumpsters" \
        --tag-keys "Manager"

This command produces no output.

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
