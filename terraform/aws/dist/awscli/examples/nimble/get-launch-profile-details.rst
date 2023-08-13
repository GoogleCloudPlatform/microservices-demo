**To list the available widgets**

The following ``get-launch-profile-details`` example lists the details about a launch profile. ::

    aws nimble get-launch-profile-details \
        --studio-id "StudioID" \
        --launch-profile-id "LaunchProfileID"

Output::

    {
        "launchProfile": {
            "arn": "arn:aws:nimble:us-west-2:123456789012:launch-profile/yeG7lDwNQEiwNTRT7DrV7Q",
            "createdAt": "2022-01-27T21:18:59+00:00",
            "createdBy": "AROA3OO2NEHCCYRNDDIFT:i-EXAMPLE11111",
            "description": "The Launch Profile for the Render workers created by StudioBuilder.",
            "ec2SubnetIds": [
                "subnet-EXAMPLE11111"
            ],
            "launchProfileId": "yeG7lDwNQEiwNTRT7DrV7Q",
            "launchProfileProtocolVersions": [
                "2021-03-31"
            ],
            "name": "RenderWorker-Default",
            "state": "READY",
            "statusCode": "LAUNCH_PROFILE_CREATED",
            "statusMessage": "Launch Profile has been created",
            "streamConfiguration": {
                "clipboardMode": "ENABLED",
                "ec2InstanceTypes": [
                    "g4dn.4xlarge",
                    "g4dn.8xlarge"
                ],
                "maxSessionLengthInMinutes": 690,
                "maxStoppedSessionLengthInMinutes": 0,
                "streamingImageIds": [
                    "Cw_jXnp1QcSSXhE2hkNRoQ",
                    "YGXAqgoWTnCNSV8VP20sHQ"
                ]
            },
            "studioComponentIds": [
                "_hR_-RaAReSOjAnLakbX7Q",
                "vQ5w_TbIRayPkAZgcbyYRA",
                "ZQuMxN99Qfa_Js6ma9TwdA",
                "45KjOSPPRzK2OyvpCuQ6qw"
            ],
            "tags": {
                "resourceArn": "arn:aws:nimble:us-west-2:123456789012:launch-profile/yeG7lDwNQEiwNTRT7DrV7Q"
            },
            "updatedAt": "2022-01-27T21:19:13+00:00",
            "updatedBy": "AROA3OO2NEHCCYRNDDIFT:i-00b98256b04d9e989",
            "validationResults": [
                {
                    "state": "VALIDATION_SUCCESS",
                    "statusCode": "VALIDATION_SUCCESS",
                    "statusMessage": "The validation succeeded.",
                    "type": "VALIDATE_ACTIVE_DIRECTORY_STUDIO_COMPONENT"
                },
                {
                    "state": "VALIDATION_SUCCESS",
                    "statusCode": "VALIDATION_SUCCESS",
                    "statusMessage": "The validation succeeded.",
                    "type": "VALIDATE_SUBNET_ASSOCIATION"
                },
                {
                    "state": "VALIDATION_SUCCESS",
                    "statusCode": "VALIDATION_SUCCESS",
                    "statusMessage": "The validation succeeded.",
                    "type": "VALIDATE_NETWORK_ACL_ASSOCIATION"
                },
                {
                    "state": "VALIDATION_SUCCESS",
                    "statusCode": "VALIDATION_SUCCESS",
                    "statusMessage": "The validation succeeded.",
                    "type": "VALIDATE_SECURITY_GROUP_ASSOCIATION"
                }
            ]
        },
        "streamingImages": [
            {
                "arn": "arn:aws:nimble:us-west-2:123456789012:streaming-image/Cw_jXnp1QcSSXhE2hkNRoQ",
                "description": "Base windows image for NimbleStudio",
                "ec2ImageId": "ami-EXAMPLE11111",
                "eulaIds": [
                    "gJZLygd-Srq_5NNbSfiaLg",
                    "ggK2eIw6RQyt8PIeeOlD3g",
                    "a-D9Wc0VQCKUfxAinCDxaw",
                    "RvoNmVXiSrS4LhLTb6ybkw",
                    "wtp85BcSTa2NZeNRnMKdjw",
                    "Rl-J0fM5Sl2hyIiwWIV6hw"
                ],
                "name": "NimbleStudioWindowsStreamImage",
                "owner": "amazon",
                "platform": "WINDOWS",
                "state": "READY",
                "streamingImageId": "Cw_jXnp1QcSSXhE2hkNRoQ",
                "tags": {
                    "resourceArn": "arn:aws:nimble:us-west-2:123456789012:streaming-image/Cw_jXnp1QcSSXhE2hkNRoQ"
                }
            },
            {
                "arn": "arn:aws:nimble:us-west-2:123456789012:streaming-image/YGXAqgoWTnCNSV8VP20sHQ",
                "description": "Base linux image for NimbleStudio",
                "ec2ImageId": "ami-EXAMPLE11111",
                "eulaIds": [
                    "gJZLygd-Srq_5NNbSfiaLg",
                    "ggK2eIw6RQyt8PIeeOlD3g",
                    "a-D9Wc0VQCKUfxAinCDxaw",
                    "RvoNmVXiSrS4LhLTb6ybkw",
                    "wtp85BcSTa2NZeNRnMKdjw",
                    "Rl-J0fM5Sl2hyIiwWIV6hw"
                ],
                "name": "NimbleStudioLinuxStreamImage",
                "owner": "amazon",
                "platform": "LINUX",
                "state": "READY",
                "streamingImageId": "YGXAqgoWTnCNSV8VP20sHQ",
                "tags": {
                    "resourceArn": "arn:aws:nimble:us-west-2:123456789012:streaming-image/YGXAqgoWTnCNSV8VP20sHQ"
                }
            }
        ],
        "studioComponentSummaries": [
            {
                "description": "FSx for Windows",
                "name": "FSxWindows",
                "studioComponentId": "ZQuMxN99Qfa_Js6ma9TwdA",
                "subtype": "AMAZON_FSX_FOR_WINDOWS",
                "type": "SHARED_FILE_SYSTEM"
            },
            {
                "description": "Instance configuration studio component.",
                "name": "InstanceConfiguration",
                "studioComponentId": "vQ5w_TbIRayPkAZgcbyYRA",
                "subtype": "CUSTOM",
                "type": "CUSTOM"
            },
            {
                "name": "ActiveDirectory",
                "studioComponentId": "_hR_-RaAReSOjAnLakbX7Q",
                "subtype": "AWS_MANAGED_MICROSOFT_AD",
                "type": "ACTIVE_DIRECTORY"
            },
            {
                "description": "Render farm running Deadline",
                "name": "RenderFarm",
                "studioComponentId": "45KjOSPPRzK2OyvpCuQ6qw",
                "subtype": "CUSTOM",
                "type": "COMPUTE_FARM"
            }
        ]
    }

For more information, see `Creating launch profiles <https://docs.aws.amazon.com/nimble-studio/latest/userguide/creating-launch-profiles.html>`__ in the *Amazon Nimble Studio User Guide*.