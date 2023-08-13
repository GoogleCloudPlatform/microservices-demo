**To respond to an authorization challenge**

This example responds to an authorization challenge initiated with `initiate-auth`_. It is a response to the NEW_PASSWORD_REQUIRED challenge. 
It sets a password for user jane@example.com.

Command::

  aws cognito-idp respond-to-auth-challenge --client-id 3n4b5urk1ft4fl3mg5e62d9ado --challenge-name NEW_PASSWORD_REQUIRED --challenge-responses USERNAME=jane@example.com,NEW_PASSWORD="password" --session "SESSION_TOKEN"

Output::

  {
    "ChallengeParameters": {},
    "AuthenticationResult": {
        "AccessToken": "ACCESS_TOKEN",
        "ExpiresIn": 3600,
        "TokenType": "Bearer",
        "RefreshToken": "REFRESH_TOKEN",
        "IdToken": "ID_TOKEN",
        "NewDeviceMetadata": {
            "DeviceKey": "us-west-2_fec070d2-fa88-424a-8ec8-b26d7198eb23",
            "DeviceGroupKey": "-wt2ha1Zd"
        }
    }
  }
  
.. _`initiate-auth`: https://docs.aws.amazon.com/cli/latest/reference/cognito-idp/initiate-auth.html