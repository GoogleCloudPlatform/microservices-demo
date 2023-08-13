**To view a list of user profiles**

The following ``list-user-profiles`` example retrieves a list of all user profiles in the current Region. ::

    aws codestar list-user-profiles

Output::

    {
        "userProfiles": [
            {
                "userArn": "arn:aws:iam::123456789012:user/admin",
                "displayName": "me",
                "emailAddress": "me@example.com",
                "sshPublicKey": ""
            },
            {
                "userArn": "arn:aws:iam::123456789012:user/intern",
                "displayName": "Intern",
                "emailAddress": "intern@example.com",
                "sshPublicKey": "intern"
            }
        ]
    }
