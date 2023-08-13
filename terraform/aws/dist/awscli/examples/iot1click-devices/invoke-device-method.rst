**To invoke a device method on a device**

The following ``invoke-device-method`` example invokes the specified method on a device. ::

    aws iot1click-devices invoke-device-method \
        --cli-input-json file://invoke-device-method.json

Contents of ``invoke-device-method.json``::

   {
       "DeviceId": "G030PM0123456789",
       "DeviceMethod": {
           "DeviceType": "device",
           "MethodName": "getDeviceHealthParameters"
       }
   }

Output::

    {
        "DeviceMethodResponse": "{\"remainingLife\": 99.8}"
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
