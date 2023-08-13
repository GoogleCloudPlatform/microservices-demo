**To create a user pool client**

This example creates a new user pool client with two explicit authorization flows: USER_PASSWORD_AUTH and ADMIN_NO_SRP_AUTH.

Command::

  aws cognito-idp create-user-pool-client --user-pool-id us-west-2_aaaaaaaaa  --client-name MyNewClient --no-generate-secret --explicit-auth-flows "USER_PASSWORD_AUTH" "ADMIN_NO_SRP_AUTH"
  
Output::

  {
    "UserPoolClient": {
        "UserPoolId": "us-west-2_aaaaaaaaa",
        "ClientName": "MyNewClient",
        "ClientId": "6p3bs000no6a4ue1idruvd05ad",
        "LastModifiedDate": 1548697449.497,
        "CreationDate": 1548697449.497,
        "RefreshTokenValidity": 30,
        "ExplicitAuthFlows": [
            "USER_PASSWORD_AUTH",
            "ADMIN_NO_SRP_AUTH"
        ],
        "AllowedOAuthFlowsUserPoolClient": false
    }
  }

