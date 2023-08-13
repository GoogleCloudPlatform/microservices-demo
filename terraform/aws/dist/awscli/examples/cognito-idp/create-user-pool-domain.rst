**To create a user pool domain**

This example creates a new user pool domain. with two explicit authorization flows: USER_PASSWORD_AUTH and ADMIN_NO_SRP_AUTH.

Command::

  aws cognito-idp create-user-pool-domain --user-pool-id us-west-2_aaaaaaaaa  --domain my-new-domain
  
