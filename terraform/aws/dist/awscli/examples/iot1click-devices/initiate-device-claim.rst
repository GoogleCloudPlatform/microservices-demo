**To initiate a claim request for an AWS IoT 1-Click device using a device ID**

The following ``initiate-device-claim`` example initiates a claim request for the specified AWS IoT 1-Click device using a device ID (instead of a claim code). ::

    aws iot1click-devices initiate-device-claim \
        --device-id G030PM0123456789

Output::

    {
        "State": "CLAIM_INITIATED"
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
