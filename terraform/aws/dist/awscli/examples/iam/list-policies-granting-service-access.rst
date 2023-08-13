**To list the policies that grant a principal access to the specified service**

The following ``list-policies-granting-service-access`` example retrieves the list of policies that grant the IAM user ``sofia`` access to AWS CodeCommit service. ::

    aws iam list-policies-granting-service-access \
        --arn arn:aws:iam::123456789012:user/sofia \
        --service-namespaces codecommit

Output::

    {
        "PoliciesGrantingServiceAccess": [
            {
                "ServiceNamespace": "codecommit",
                "Policies": [
                    {
                        "PolicyName": "Grant-Sofia-Access-To-CodeCommit",
                        "PolicyType": "INLINE",
                        "EntityType": "USER",
                        "EntityName": "sofia"
                    }
                ]
            }
        ],
        "IsTruncated": false
    }

For more information, see `Using IAM with CodeCommit: Git Credentials, SSH Keys, and AWS Access Keys <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_ssh-keys.html>`_ in the *AWS IAM User Guide*.
