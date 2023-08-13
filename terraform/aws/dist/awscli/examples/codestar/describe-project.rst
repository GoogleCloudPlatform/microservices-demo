**To view a project**

The following ``describe-project`` example retrieves details about the specified project. ::

    aws codestar describe-project \
        --id my-project

Output::

    {
        "name": "my project",
        "id": "my-project",
        "arn": "arn:aws:codestar:us-west-2:123456789012:project/my-project",
        "description": "My first CodeStar project.",
        "createdTimeStamp": 1572547510.128,
        "status": {
            "state": "CreateComplete"
        }
    }
