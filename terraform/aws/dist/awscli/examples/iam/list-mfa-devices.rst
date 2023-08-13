**To list all MFA devices for a specified user**

This example returns details about the MFA device assigned to the IAM user ``Bob``::

  aws iam list-mfa-devices --user-name Bob 

Output::

  {
    "MFADevices": [
      {
        "UserName": "Bob",
        "SerialNumber": "arn:aws:iam::123456789012:mfa/BobsMFADevice",
        "EnableDate": "2015-06-16T22:36:37Z"
      }
    ]
  }

For more information, see `Using Multi-Factor Authentication (MFA) Devices with AWS`_ in the *Using IAM* guide.

.. _`Using Multi-Factor Authentication (MFA) Devices with AWS`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_ManagingMFA.html
