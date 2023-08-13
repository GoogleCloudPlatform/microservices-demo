**To list all devices in a placement contained in a project**

The following ``get-devices-in-placement`` example lists all devices in a the specified placement contained in the specified project. ::

    aws iot1click-projects get-devices-in-placement \
        --project-name AnytownDumpsters \
        --placement-name customer217

Output::

    {
        "devices": {
            "empty-dumpster-request": "G030PM0123456789"
        }
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
