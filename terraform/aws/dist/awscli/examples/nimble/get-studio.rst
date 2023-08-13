**To get information about your studio**

The following ``get-studio`` example lists the studios in your AWS account. ::

    aws nimble get-studio \
        --studio-id "StudioID"

Output::

    {
        "studio": {
            "adminRoleArn": "arn:aws:iam::123456789012:role/studio-admin-role",
            "arn": "arn:aws:nimble:us-west-2:123456789012:studio/stid-EXAMPLE11111",
            "createdAt": "2022-01-27T20:29:35+00:00",
            "displayName": "studio-name",
            "homeRegion": "us-west-2",
            "ssoClientId": "a1b2c3d4-5678-90ab-cdef-EXAMPLE11111",
            "state": "READY",
            "statusCode": "STUDIO_CREATED",
            "statusMessage": "The studio has been created successfully ",
            "studioEncryptionConfiguration": {
                "keyType": "AWS_OWNED_KEY"
            },
            "studioId": "us-west-2:stid-EXAMPLE11111",
            "studioName": "studio-name",
            "studioUrl": "https://studio-name.nimblestudio.us-west-2.amazonaws.com",
            "tags": {},
            "updatedAt": "2022-01-27T20:29:37+00:00",
            "userRoleArn": "arn:aws:iam::123456789012:role/studio-user-role"
        }
    }

For more information, see `What is Amazon Nimble Studio? <https://docs.aws.amazon.com/nimble-studio/latest/userguide/what-is-nimble-studio.html>`__ in the *Amazon Nimble Studio User Guide*.
