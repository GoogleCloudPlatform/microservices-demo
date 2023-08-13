**To view resources**

The following ``list-resources`` example retrieves a list of resources for the specified project. ::

    aws codestar list-resources \
        --id my-project

Output::

    {
        "resources": [
            {
                "id": "arn:aws:execute-api:us-east-2:123456789012:r3wxmplbv8"
            },
            {
                "id": "arn:aws:codedeploy:us-east-2:123456789012:application:awscodestar-my-project-lambda-ServerlessDeploymentApplication-PF0LXMPL1KA0"
            },
            {
                "id": "arn:aws:s3:::aws-codestar-us-east-2-123456789012-my-project-pipe"
            },
            {
                "id": "arn:aws:lambda:us-east-2:123456789012:function:awscodestar-my-project-lambda-GetHelloWorld-16W3LVXMPLNNS"
            },
            {
                "id": "arn:aws:cloudformation:us-east-2:123456789012:stack/awscodestar-my-project-lambda/b4904ea0-fc20-xmpl-bec6-029123b1cc42"
            },
            {
                "id": "arn:aws:cloudformation:us-east-2:123456789012:stack/awscodestar-my-project/1b133f30-fc20-xmpl-a93a-0688c4290cb8"
            },
            {
                "id": "arn:aws:iam::123456789012:role/CodeStarWorker-my-project-ToolChain"
            },
            {
                "id": "arn:aws:iam::123456789012:policy/CodeStar_my-project_PermissionsBoundary"
            },
            {
                "id": "arn:aws:s3:::aws-codestar-us-east-2-123456789012-my-project-app"
            },
            {
                "id": "arn:aws:codepipeline:us-east-2:123456789012:my-project-Pipeline"
            },
            {
                "id": "arn:aws:codedeploy:us-east-2:123456789012:deploymentgroup:my-project/awscodestar-my-project-lambda-GetHelloWorldDeploymentGroup-P7YWXMPLT0QB"
            },
            {
                "id": "arn:aws:iam::123456789012:role/CodeStar-my-project-Execution"
            },
            {
                "id": "arn:aws:iam::123456789012:role/CodeStarWorker-my-project-CodeDeploy"
            },
            {
                "id": "arn:aws:codebuild:us-east-2:123456789012:project/my-project"
            },
            {
                "id": "arn:aws:iam::123456789012:role/CodeStarWorker-my-project-CloudFormation"
            },
            {
                "id": "arn:aws:codecommit:us-east-2:123456789012:Go-project"
            }
        ]
    }
