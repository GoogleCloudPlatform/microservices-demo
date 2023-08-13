**To view projects**

The following ``list-projects`` example retrieves a list of projects in the current Region. ::

    aws codestar list-projects

Output::

    {
        "projects": [
            {
                "projectId": "intern-projects",
                "projectArn": "arn:aws:codestar:us-west-2:123456789012:project/intern-projects"
            },
            {
                "projectId": "my-project",
                "projectArn": "arn:aws:codestar:us-west-2:123456789012:project/my-project"
            }
        ]
    }
