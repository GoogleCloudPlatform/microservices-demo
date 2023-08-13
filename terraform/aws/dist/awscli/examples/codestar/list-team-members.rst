**To view a list of team members**

The following ``list-team-members`` example retrieves a list of users associated with the specified project. ::

    aws codestar list-team-members \
        --project-id my-project

Output::

    {
        "teamMembers": [
            {
                "userArn": "arn:aws:iam::123456789012:user/admin",
                "projectRole": "Owner",
                "remoteAccessAllowed": false
            },
            {
                "userArn": "arn:aws:iam::123456789012:user/intern",
                "projectRole": "Contributor",
                "remoteAccessAllowed": false
            }
        ]
    }
