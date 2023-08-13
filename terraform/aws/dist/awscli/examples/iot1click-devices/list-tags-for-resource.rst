**To list the tags for a device**

The following ``list-tags-for-resource`` example list the tags for the specified device. ::

    aws iot1click-devices list-tags-for-resource \
        --resource-arn "arn:aws:iot1click:us-west-2:012345678901:devices/G030PM0123456789"

Output::

    {
        "Tags": {
            "Driver Phone": "123-555-0199",
            "Driver": "Jorge Souza"
        }
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
