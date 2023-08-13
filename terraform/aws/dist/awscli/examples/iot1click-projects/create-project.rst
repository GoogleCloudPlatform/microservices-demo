**To create an AWS IoT 1-Click project for zero or more placements**

The following ``create-project`` example creates an AWS IoT 1-Click project for a placement.

    aws iot1click-projects create-project \
        --cli-input-json file://create-project.json

Contents of ``create-project.json``::

    {
         "projectName": "AnytownDumpsters",
         "description": "All dumpsters in the Anytown region.",
         "placementTemplate": {
             "defaultAttributes": {
                 "City" : "Anytown"
             },
             "deviceTemplates": {
                 "empty-dumpster-request" : {
                     "deviceType": "button"
                 }
             }
         }
    }

This command produces no output.

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
