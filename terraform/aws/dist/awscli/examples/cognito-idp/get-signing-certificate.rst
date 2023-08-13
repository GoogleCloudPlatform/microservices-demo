**To get a signing certificate**

This example gets a signing certificate for a user pool.

Command::

  aws cognito-idp get-signing-certificate --user-pool-id us-west-2_aaaaaaaaa 

Output::

  {
    "Certificate": "CERTIFICATE_DATA"
  }