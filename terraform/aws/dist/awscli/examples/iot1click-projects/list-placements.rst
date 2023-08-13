**To list all AWS IoT 1-Click placements for a project**

The following ``list-placements`` example lists all AWS IoT 1-Click placements for the specified project. ::

    aws iot1click-projects list-placements \
        --project-name AnytownDumpsters

Output::

    {
        "placements": [
            {
                "projectName": "AnytownDumpsters",
                "placementName": "customer217",
                "createdDate": 1563488454,
                "updatedDate": 1563488454
            }
        ]
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
