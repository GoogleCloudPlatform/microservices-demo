**To deactivate an MFA device**

This command deactivates the virtual MFA device with the ARN ``arn:aws:iam::210987654321:mfa/BobsMFADevice`` that is associated with the user ``Bob``::

  aws iam deactivate-mfa-device --user-name Bob --serial-number arn:aws:iam::210987654321:mfa/BobsMFADevice


For more information, see `Using Multi-Factor Authentication (MFA) Devices with AWS`_ in the *Using IAM* guide.

.. _`Using Multi-Factor Authentication (MFA) Devices with AWS`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_ManagingMFA.html