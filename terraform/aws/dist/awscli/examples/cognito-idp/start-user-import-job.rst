**To start a user import job**

This example starts a user input job. 

For more information about importing users, see `Importing Users into User Pools From a CSV File`_.

Command::

  aws cognito-idp start-user-import-job --user-pool-id us-west-2_aaaaaaaaa --job-id import-TZqNQvDRnW

Output::

  {
    "UserImportJob": {
        "JobName": "import-Test10",
        "JobId": "import-lmpxSOuIzH",
        "UserPoolId": "us-west-2_aaaaaaaaa",
        "PreSignedUrl": "PRE_SIGNED_URL",
        "CreationDate": 1548278378.928,
        "StartDate": 1548278397.334,
        "Status": "Pending",
        "CloudWatchLogsRoleArn": "arn:aws:iam::111111111111:role/CognitoCloudWatchLogsRole",
        "ImportedUsers": 0,
        "SkippedUsers": 0,
        "FailedUsers": 0
    }
  }
  
.. _`Importing Users into User Pools From a CSV File`: https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-using-import-tool.html