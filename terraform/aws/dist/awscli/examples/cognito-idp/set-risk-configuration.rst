**To set risk configuration**

This example sets the risk configuration for a user pool. It sets the sign-up event action to NO_ACTION. 

Command::

  aws cognito-idp set-risk-configuration --user-pool-id us-west-2_aaaaaaaaa  --compromised-credentials-risk-configuration EventFilter=SIGN_UP,Actions={EventAction=NO_ACTION}

Output::

  {
    "RiskConfiguration": {
        "UserPoolId": "us-west-2_aaaaaaaaa",
        "CompromisedCredentialsRiskConfiguration": {
            "EventFilter": [
                "SIGN_UP"
            ],
            "Actions": {
                "EventAction": "NO_ACTION"
            }
        }
    }
  }