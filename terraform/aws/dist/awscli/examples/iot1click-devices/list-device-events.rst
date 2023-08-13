**To list a device's events for a specified time range**

The following ``list-device-events`` example lists the specified device's events for the specified time range. ::

    aws iot1click-devices list-device-events \
        --device-id G030PM0123456789 \
        --from-time-stamp 2019-07-17T15:45:12.880Z --to-time-stamp 2019-07-19T15:45:12.880Z

Output::

    {
        "Events": [
            {
                "Device": {
                    "Attributes": {},
                    "DeviceId": "G030PM0123456789",
                    "Type": "button"
                },
                "StdEvent": "{\"clickType\": \"SINGLE\", \"reportedTime\": \"2019-07-18T23:47:55.015Z\", \"certificateId\": \"fe8798a6c97c62ef8756b80eeefdcf2280f3352f82faa8080c74cc4f4a4d1811\", \"remainingLife\": 99.85000000000001, \"testMode\": false}"
            },
            {
                "Device": {
                    "Attributes": {},
                    "DeviceId": "G030PM0123456789",
                    "Type": "button"
                },
                "StdEvent": "{\"clickType\": \"DOUBLE\", \"reportedTime\": \"2019-07-19T00:14:41.353Z\", \"certificateId\": \"fe8798a6c97c62ef8756b80eeefdcf2280f3352f82faa8080c74cc4f4a4d1811\", \"remainingLife\": 99.8, \"testMode\": false}"
            }
        ]
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
