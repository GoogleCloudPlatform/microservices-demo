**To simulate the effects of an arbitrary IAM policy**

The following ``simulate-principal-policy`` shows how to simulate a user calling an API action and determining whether the policies associated with that user allow or deny the action. In the following example, the user has a policy that allows only the ``codecommit:ListRepositories`` action. ::

    aws iam simulate-principal-policy \
        --policy-source-arn arn:aws:iam::123456789012:user/alejandro \
        --action-names codecommit:ListRepositories

Output::

    {
        "EvaluationResults": [
            {
                "EvalActionName": "codecommit:ListRepositories",
                "EvalResourceName": "*",
                "EvalDecision": "allowed",
                "MatchedStatements": [
                    {
                        "SourcePolicyId": "Grant-Access-To-CodeCommit-ListRepo",
                        "StartPosition": {
                            "Line": 3,
                            "Column": 19
                        },
                        "EndPosition": {
                            "Line": 9,
                            "Column": 10
                        }
                    }
                ],
                "MissingContextValues": []
            }
        ]
    }

The following ``simulate-custom-policy`` example shows the results of simulating a command that is prohibited by one of the user's policies. In the following example, the user has a policy that permits access to a DynamoDB database only after a certain date and time. The simulation has the user attempting to access the database with an ``aws:CurrentTime`` value that is earlier than the policy's condition permits. ::

    aws iam simulate-principal-policy \
        --policy-source-arn arn:aws:iam::123456789012:user/alejandro \
        --action-names dynamodb:CreateBackup \
        --context-entries "ContextKeyName='aws:CurrentTime',ContextKeyValues='2018-04-25T11:00:00Z',ContextKeyType=date"

Output::

    {
        "EvaluationResults": [
            {
                "EvalActionName": "dynamodb:CreateBackup",
                "EvalResourceName": "*",
                "EvalDecision": "implicitDeny",
                "MatchedStatements": [],
                "MissingContextValues": []
            }
        ]
    }

For more information, see `Testing IAM Policies with the IAM Policy Simulator`_ in the *AWS IAM User Guide*

.. _`Testing IAM Policies with the IAM Policy Simulator`: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_testing-policies.html
