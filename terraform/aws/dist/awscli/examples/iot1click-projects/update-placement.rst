**To update the "attributes" key-value pairs of a placement**

The following ``update-placement`` example update the "attributes" key-value pairs of a placement. ::

    aws iot1click-projects update-placement \
        --cli-input-json file://update-placement.json

Contents of ``update-placement.json``::

    {
        "projectName": "AnytownDumpsters",
        "placementName": "customer217",
        "attributes": {
            "phone": "123-456-7890",
            "location": "123 Any Street Anytown, USA 10001"
        }
    }

This command produces no output.

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
