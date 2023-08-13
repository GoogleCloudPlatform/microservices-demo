**To describe the status of an instance**

This example describes the current status of the specified instance.

Command::

  aws ec2 describe-instance-status --instance-id i-1234567890abcdef0

Output::

  {
      "InstanceStatuses": [
          {
              "InstanceId": "i-1234567890abcdef0",
              "InstanceState": {
                  "Code": 16,
                  "Name": "running"
              },
              "AvailabilityZone": "us-east-1d",
              "SystemStatus": {
                  "Status": "ok",
                  "Details": [
                      {
                          "Status": "passed",
                          "Name": "reachability"
                      }
                  ]
              },
              "InstanceStatus": {
                  "Status": "ok",
                  "Details": [
                      {
                          "Status": "passed",
                          "Name": "reachability"
                      }
                  ]
              }
          }
      ]
  }
