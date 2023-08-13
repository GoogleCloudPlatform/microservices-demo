**To unclaim (deregister) a device from your AWS account**

The following ``unclaim-device`` example unclaims (deregisters) the specified device from your AWS account. ::

    aws iot1click-devices unclaim-device \
        --device-id G030PM0123456789

Output::

    {
        "State": "UNCLAIMED"
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
