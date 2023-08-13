**To initiate authorization**

This example initiates authorization using the ADMIN_NO_SRP_AUTH flow for username jane@example.com

The client must have sign-in API for server-based authentication (ADMIN_NO_SRP_AUTH) enabled.

Use the session information in the return value to call `admin-respond-to-auth-challenge`_.

Command::

  aws cognito-idp admin-initiate-auth --user-pool-id us-west-2_aaaaaaaaa --client-id 3n4b5urk1ft4fl3mg5e62d9ado --auth-flow ADMIN_NO_SRP_AUTH --auth-parameters USERNAME=jane@example.com,PASSWORD=password
  
Output::

  {
    "ChallengeName": "NEW_PASSWORD_REQUIRED",
    "Session": "SESSION",
    "ChallengeParameters": {
        "USER_ID_FOR_SRP": "84514837-dcbc-4af1-abff-f3c109334894",
        "requiredAttributes": "[]",
        "userAttributes": "{\"email_verified\":\"true\",\"phone_number_verified\":\"true\",\"phone_number\":\"+01xxx5550100\",\"email\":\"jane@example.com\"}"
    }
  }
  
.. _`admin-respond-to-auth-challenge`: https://docs.aws.amazon.com/cli/latest/reference/cognito-idp/admin-respond-to-auth-challenge.html