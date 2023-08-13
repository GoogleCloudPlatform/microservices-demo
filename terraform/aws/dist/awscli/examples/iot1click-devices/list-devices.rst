**To list the devices of a specified type**

The following ``list-devices`` example lists the devices of a specified type. ::

    aws iot1click-devices list-devices \
        --device-type button

This command produces no output.

Output::

    {
        "Devices": [
            {
                "remainingLife": 99.9,
                "attributes": {
                    "arn": "arn:aws:iot1click:us-west-2:123456789012:devices/G030PM0123456789",
                    "type": "button",
                    "deviceId": "G030PM0123456789",
                    "enabled": false
                }
            }
        ]
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
