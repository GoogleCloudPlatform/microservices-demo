**To create a user profile**

The following ``create-user-profile`` example creates a user profile for the IAM user with the specified ARN. ::

    aws codestar create-user-profile \
        --user-arn arn:aws:iam::123456789012:user/intern \
        --display-name Intern \
        --email-address intern@example.com

Output::

    {
        "userArn": "arn:aws:iam::123456789012:user/intern",
        "displayName": "Intern",
        "emailAddress": "intern@example.com",
        "sshPublicKey": "",
        "createdTimestamp": 1572552308.607,
        "lastModifiedTimestamp": 1572552308.607
    }
