**To add tags to a project resource**

The following ``tag-resource`` example adds two tags to the specified project resource. ::

    aws iot1click-projects tag-resource \
        --cli-input-json file://devices-tag-resource.json
    
Contents of ``devices-tag-resource.json``::

    {
        "resourceArn": "arn:aws:iot1click:us-west-2:123456789012:projects/AnytownDumpsters",
        "tags": {
            "Account": "45215",
            "Manager": "Li Juan"
        }
    }

This command produces no output.

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
