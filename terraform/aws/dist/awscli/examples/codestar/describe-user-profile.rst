**To view a user profile**

The following ``describe-user-profile`` example retrieves details about the user profile for the user with the specified ARN. ::

    aws codestar describe-user-profile \
        --user-arn arn:aws:iam::123456789012:user/intern

Output::

    {
        "userArn": "arn:aws:iam::123456789012:user/intern",
        "displayName": "Intern",
        "emailAddress": "intern@example.com",
        "sshPublicKey": "intern",
        "createdTimestamp": 1572552308.607,
        "lastModifiedTimestamp": 1572553495.47
    }
