**To list the available widgets**

The following ``list-launch-profiles`` example lists the launch profiles in your AWS account. ::

    aws nimble list-launch-profiles \
        --studio-id "StudioID"

Output::

    {
        "launchProfiles": [
            {
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
                "tags": {},
                "updatedAt": "2022-01-27T21:19:13+00:00",
                "updatedBy": "AROA3OO2NEHCCYRNDDIFT:i-EXAMPLE11111",
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
            {
                "arn": "arn:aws:nimble:us-west-2:123456789012:launch-profile/jDCIm1jRSaa9e44PZ3w7gg",
                "createdAt": "2022-01-27T21:19:26+00:00",
                "createdBy": "AROA3OO2NEHCCYRNDDIFT:i-EXAMPLE11111",
                "description": "This Workstation Launch Profile was created by StudioBuilder",
                "ec2SubnetIds": [
                    "subnet-046f4205ae535b2cc"
                ],
                "launchProfileId": "jDCIm1jRSaa9e44PZ3w7gg",
                "launchProfileProtocolVersions": [
                    "2021-03-31"
                ],
                "name": "Workstation-Default",
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
                    "yJSbsHXAQYWk9FXLNusXlQ",
                    "45KjOSPPRzK2OyvpCuQ6qw"
                ],
                "tags": {},
                "updatedAt": "2022-01-27T21:19:40+00:00",
                "updatedBy": "AROA3OO2NEHCCYRNDDIFT:i-EXAMPLE11111",
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
            }
        ]
    }

For more information, see `Creating launch profiles <https://docs.aws.amazon.com/nimble-studio/latest/userguide/creating-launch-profiles.html>`__ in the *Amazon Nimble Studio User Guide*.