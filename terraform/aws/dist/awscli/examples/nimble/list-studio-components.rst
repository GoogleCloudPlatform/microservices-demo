**To list the available widgets**

The following ``list-studio-components`` example lists the studio components in your AWS account. ::

    aws nimble list-studio-components \
        --studio-id "StudioID"

Output::

    {
        "studioComponents": [
            {
                "arn": "arn:aws:nimble:us-west-2:123456789012:studio-component/ZQuMxN99Qfa_Js6ma9TwdA",
                "configuration": {
                    "sharedFileSystemConfiguration": {
                        "fileSystemId": "fs-EXAMPLE11111",
                        "linuxMountPoint": "/mnt/fsxshare",
                        "shareName": "share",
                        "windowsMountDrive": "Z"
                    }
                },
                "createdAt": "2022-01-27T21:15:34+00:00",
                "createdBy": "AROA3OO2NEHCCYRNDDIFT:i-EXAMPLE11111",
                "description": "FSx for Windows",
                "ec2SecurityGroupIds": [
                    "sg-EXAMPLE11111"
                ],
                "name": "FSxWindows",
                "state": "READY",
                "statusCode": "STUDIO_COMPONENT_CREATED",
                "statusMessage": "Studio Component has been created",
                "studioComponentId": "ZQuMxN99Qfa_Js6ma9TwdA",
                "subtype": "AMAZON_FSX_FOR_WINDOWS",
                "tags": {},
                "type": "SHARED_FILE_SYSTEM",
                "updatedAt": "2022-01-27T21:15:35+00:00",
                "updatedBy": "AROA3OO2NEHCCYRNDDIFT:i-EXAMPLE11111"
            },
        ...
    }

For more information, see `How StudioBuilder works with Amazon Nimble Studio <https://docs.aws.amazon.com/nimble-studio/latest/userguide/what-is-studiobuilder.html>`__ in the *Amazon Nimble Studio User Guide*.