**To claim one or more AWS IoT 1-Click devices using a claim code**

The following ``claim-devices-by-claim-code`` example claims the specified AWS IoT 1-Click device using a claim code (instead of a device ID). ::

    aws iot1click-devices claim-devices-by-claim-code \
        --claim-code C-123EXAMPLE

Output::

    {
       "Total": 9
       "ClaimCode": "C-123EXAMPLE"
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
