**To remove tags from a device AWS resource**

The following ``untag-resource`` example removes the tags with the names ``Driver Phone`` and ``Driver`` from the specified device resource. ::

    aws iot1click-devices untag-resource \
        --resource-arn "arn:aws:iot1click:us-west-2:123456789012:projects/AnytownDumpsters" \
        --tag-keys "Driver Phone" "Driver"


This command produces no output.

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
