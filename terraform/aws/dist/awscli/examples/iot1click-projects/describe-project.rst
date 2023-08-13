**To describe an AWS IoT 1-Click project**

The following ``describe-project`` example describes the specified AWS IoT 1-Click project. ::

    aws iot1click-projects describe-project \
        --project-name AnytownDumpsters

Output::

    {
        "project": {
            "arn": "arn:aws:iot1click:us-west-2:012345678901:projects/AnytownDumpsters",
            "projectName": "AnytownDumpsters",
            "description": "All dumpsters in the Anytown region.",
            "createdDate": 1563483100,
            "updatedDate": 1563483100,
            "placementTemplate": {
                "defaultAttributes": {
                    "City": "Anytown"
                },
                "deviceTemplates": {
                    "empty-dumpster-request": {
                        "deviceType": "button",
                        "callbackOverrides": {}
                    }
                }
            },
            "tags": {}
        }
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
