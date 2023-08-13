**To describe a device**

The following ``describe-device`` example describes the specified device. ::

    aws iot1click-devices describe-device \
        --device-id G030PM0123456789

Output::

   {
       "DeviceDescription": {
           "Arn": "arn:aws:iot1click:us-west-2:012345678901:devices/G030PM0123456789",
           "Attributes": {
               "projectRegion": "us-west-2",
               "projectName": "AnytownDumpsters",
               "placementName": "customer217",
               "deviceTemplateName": "empty-dumpster-request"
           },
           "DeviceId": "G030PM0123456789",
           "Enabled": false,
           "RemainingLife": 99.9,
           "Type": "button",
           "Tags": {}
       }
   }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
