**To update a user pool client**

This example updates the name of a user pool client. It also adds a writeable attribute "nickname".

Command::

  aws cognito-idp update-user-pool-client --user-pool-id us-west-2_aaaaaaaaa --client-id 3n4b5urk1ft4fl3mg5e62d9ado --client-name "NewClientName" --write-attributes "nickname"

Output::

  {
    "UserPoolClient": {
        "UserPoolId": "us-west-2_aaaaaaaaa",
        "ClientName": "NewClientName",
        "ClientId": "3n4b5urk1ft4fl3mg5e62d9ado",
        "LastModifiedDate": 1548802761.334,
        "CreationDate": 1548178931.258,
        "RefreshTokenValidity": 30,
        "WriteAttributes": [
            "nickname"
        ],
        "AllowedOAuthFlowsUserPoolClient": false
    }
  }