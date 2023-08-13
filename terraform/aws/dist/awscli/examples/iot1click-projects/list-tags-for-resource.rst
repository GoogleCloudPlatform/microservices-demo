**To list the tags for a project resource**

The following ``list-tags-for-resource`` example list the tags for the specified project resource. ::

    aws iot1click-projects list-tags-for-resource \
        --resource-arn "arn:aws:iot1click:us-west-2:123456789012:projects/AnytownDumpsters"

Output::

    {
        "tags": {
            "Manager": "Li Juan",
            "Account": "45215"
        }
    }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
