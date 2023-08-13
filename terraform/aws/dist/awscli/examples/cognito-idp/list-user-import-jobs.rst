**To list user import jobs**

This example lists user import jobs. 

For more information about importing users, see `Importing Users into User Pools From a CSV File`_.

Command::

  aws cognito-idp list-user-import-jobs --user-pool-id us-west-2_aaaaaaaaa  --max-results 20

Output::

  {
    "UserImportJobs": [
        {
            "JobName": "Test2",
            "JobId": "import-d0OnwGA3mV",
            "UserPoolId": "us-west-2_aaaaaaaaa",
            "PreSignedUrl": "PRE_SIGNED_URL",
            "CreationDate": 1548272793.069,
            "Status": "Created",
            "CloudWatchLogsRoleArn": "arn:aws:iam::111111111111:role/CognitoCloudWatchLogsRole",
            "ImportedUsers": 0,
            "SkippedUsers": 0,
            "FailedUsers": 0
        },
        {
            "JobName": "Test1",
            "JobId": "import-qQ0DCt2fRh",
            "UserPoolId": "us-west-2_aaaaaaaaa",
            "PreSignedUrl": "PRE_SIGNED_URL",
            "CreationDate": 1548271795.471,
            "Status": "Created",
            "CloudWatchLogsRoleArn": "arn:aws:iam::111111111111:role/CognitoCloudWatchLogsRole",
            "ImportedUsers": 0,
            "SkippedUsers": 0,
            "FailedUsers": 0
        },
        {
            "JobName": "import-Test1",
            "JobId": "import-TZqNQvDRnW",
            "UserPoolId": "us-west-2_aaaaaaaaa",
            "PreSignedUrl": "PRE_SIGNED_URL",
            "CreationDate": 1548271708.512,
            "StartDate": 1548277247.962,
            "CompletionDate": 1548277248.912,
            "Status": "Failed",
            "CloudWatchLogsRoleArn": "arn:aws:iam::111111111111:role/CognitoCloudWatchLogsRole",
            "ImportedUsers": 0,
            "SkippedUsers": 0,
            "FailedUsers": 1,
            "CompletionMessage": "Too many users have failed or been skipped during the import."
        }
    ]
  }
  
.. _`Importing Users into User Pools From a CSV File`: https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-using-import-tool.html