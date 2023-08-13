**To list the available methods for a device**

The following ``get-device-methods`` example lists the available methods for a device. ::

    aws iot1click-devices get-device-methods \
        --device-id G030PM0123456789

Output::

    {
        "DeviceMethods": [
            {
                "MethodName": "getDeviceHealthParameters"
            },
            {
                "MethodName": "setDeviceHealthMonitorCallback"
            },
            {
                "MethodName": "getDeviceHealthMonitorCallback"
            },
            {
                "MethodName": "setOnClickCallback"
            },
            {
                "MethodName": "getOnClickCallback"
            }
        ]
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
