**To list users**

This example lists up to 20 users.   

Command::

  aws cognito-idp list-users --user-pool-id us-west-2_aaaaaaaaa --limit 20

Output::

  {
    "Users": [
        {
            "Username": "22704aa3-fc10-479a-97eb-2af5806bd327",
            "Enabled": true,
            "UserStatus": "FORCE_CHANGE_PASSWORD",
            "UserCreateDate": 1548089817.683,
            "UserLastModifiedDate": 1548089817.683,
            "Attributes": [
                {
                    "Name": "sub",
                    "Value": "22704aa3-fc10-479a-97eb-2af5806bd327"
                },
                {
                    "Name": "email_verified",
                    "Value": "true"
                },
                {
                    "Name": "email",
                    "Value": "mary@example.com"
                }
            ]
        }
    ]
  }
