**To create a project**

The following ``create-project`` example uses a JSON input file to create a CodeStar project. ::

    aws codestar create-project \
        --cli-input-json file://create-project.json

Contents of ``create-project.json``::

    {
        "name": "Custom Project",
        "id": "custom-project",
        "sourceCode": [
            {
                "source": {
                    "s3": {
                        "bucketName": "codestar-artifacts",
                        "bucketKey": "nodejs-function.zip"
                    }
                },
                "destination": {
                    "codeCommit": {
                        "name": "codestar-custom-project"
                    }
                }
            }
        ],
        "toolchain": {
            "source": {
                "s3": {
                    "bucketName": "codestar-artifacts",
                    "bucketKey": "toolchain.yml"
                }
            },
            "roleArn": "arn:aws:iam::123456789012:role/service-role/aws-codestar-service-role",
            "stackParameters": {
                "ProjectId": "custom-project"
            }
        }
    }

Output::

    {
        "id": "my-project",
        "arn": "arn:aws:codestar:us-east-2:123456789012:project/custom-project"
    }

For a tutorial that includes sample code and templates for a custom project, see `Create a Project in AWS CodeStar with the AWS CLI<https://docs.aws.amazon.com/codestar/latest/userguide/cli-tutorial.html>`__ in the *AWS CodeStar User Guide*.
