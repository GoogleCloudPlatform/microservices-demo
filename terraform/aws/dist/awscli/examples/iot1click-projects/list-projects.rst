**To list all AWS IoT 1-Click projects**

The following ``list-projects`` example list all AWS IoT 1-Click projects in your account. ::

    aws iot1click-projects list-projects

Output::

    {
        "projects": [
            {
                "arn": "arn:aws:iot1click:us-west-2:012345678901:projects/AnytownDumpsters",
                "projectName": "AnytownDumpsters",
                "createdDate": 1563483100,
                "updatedDate": 1563483100,
                "tags": {}
            }
        ]
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
