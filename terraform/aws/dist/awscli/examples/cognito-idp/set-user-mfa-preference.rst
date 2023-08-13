**To set user MFA settings**

This example modifies the MFA delivery options. It changes the MFA delivery medium to SMS.

Command::

  aws cognito-idp set-user-mfa-preference --access-token ACCESS_TOKEN --mfa-options DeliveryMedium="SMS",AttributeName="phone_number"

