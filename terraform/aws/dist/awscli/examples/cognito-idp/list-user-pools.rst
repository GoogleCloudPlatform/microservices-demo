**To list user pools**

This example lists up to 20 user pools.   

Command::

  aws cognito-idp list-user-pools --max-results 20

Output::

  {
    "UserPools": [
        {
           "CreationDate": 1547763720.822,
           "LastModifiedDate": 1547763720.822,
           "LambdaConfig": {},
           "Id": "us-west-2_aaaaaaaaa",
           "Name": "MyUserPool"
        }
    ]
  }

