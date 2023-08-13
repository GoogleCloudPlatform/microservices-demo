**To create a virtual MFA device**

This example creates a new virtual MFA device called ``BobsMFADevice``. It creates a file that contains bootstrap information called ``QRCode.png`` 
and places it in the ``C:/`` directory. The bootstrap method used in this example is ``QRCodePNG``::


  aws iam create-virtual-mfa-device --virtual-mfa-device-name BobsMFADevice --outfile C:/QRCode.png --bootstrap-method QRCodePNG

Output::

  {
      "VirtualMFADevice": {
          "SerialNumber": "arn:aws:iam::210987654321:mfa/BobsMFADevice"
  }

For more information, see `Using Multi-Factor Authentication (MFA) Devices with AWS`_ in the *Using IAM* guide.

.. _`Using Multi-Factor Authentication (MFA) Devices with AWS`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_ManagingMFA.html