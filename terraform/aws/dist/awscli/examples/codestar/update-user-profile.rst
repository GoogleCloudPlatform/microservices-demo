**To modify a user profile**

The following ``update-user-profile`` example adds the specified SHH key to the specified user. ::

    aws codestar update-user-profile \
        --ssh-public-key intern \
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
