**To list virtual MFA devices**

The following ``list-virtual-mfa-devices`` command lists the virtual MFA devices that have been configured for the current account::

  aws iam list-virtual-mfa-devices

Output::

  {
    "VirtualMFADevices": [
      {
        "SerialNumber": "arn:aws:iam::123456789012:mfa/ExampleMFADevice"
      },
      {
        "SerialNumber": "arn:aws:iam::123456789012:mfa/Fred"
      }
    ]
  }

For more information, see `Using a Virtual MFA Device with AWS`_ in the *Using IAM* guide.

.. _`Using a Virtual MFA Device with AWS`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_VirtualMFA.html

