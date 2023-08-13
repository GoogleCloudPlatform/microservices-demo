**To describe the credit option for CPU usage of one or more instances**

This example describes the current credit option for CPU usage of the specified instance.

Command::

  aws ec2 describe-instance-credit-specifications --instance-id i-1234567890abcdef0

Output::

  {
    "InstanceCreditSpecifications": [
      {
          "InstanceId": "i-1234567890abcdef0",
          "CpuCredits": "unlimited"
      }
    ]
  }