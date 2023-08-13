**To modify a team member**

The following ``update-team-member`` example makes the specified user a contributor on a project and grants them remote access to project resources. ::

    aws codestar update-team-member \
        --project-id my-project \
        --user-arn arn:aws:iam::123456789012:user/intern \
        --project-role Contributor -\
        --remote-access-allowed

Output::

    {
        "userArn": "arn:aws:iam::123456789012:user/intern",
        "projectRole": "Contributor",
        "remoteAccessAllowed": true
    }
