**To add tags to a device AWS resource**

The following ``tag-resource`` example adds two tags to the specified resource. ::

    aws iot1click-devices tag-resource \
        --cli-input-json file://devices-tag-resource.json

Contents of ``devices-tag-resource.json``::

    {
        "ResourceArn": "arn:aws:iot1click:us-west-2:123456789012:devices/G030PM0123456789",
        "Tags": {
            "Driver": "Jorge Souza",
            "Driver Phone": "123-555-0199"
        }
    }

This command produces no output.

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
