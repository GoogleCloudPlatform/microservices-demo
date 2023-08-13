**To lists the instance profiles for the account**

The following ``list-instance-profiles`` command lists the instance profiles that are associated with the current account::

  aws iam list-instance-profiles

Output::

  {
    "InstanceProfiles": [
      {
        "InstanceProfileId": "AIPAIXEU4NUHUPEXAMPLE",
        "Roles": [
          {
            "AssumeRolePolicyDocument": {
              "Version": "2012-10-17",
              "Statement": [
                {
                  "Action": "sts:AssumeRole",
                  "Principal": {
                    "Service": "ec2.amazonaws.com"
                  },
                  "Effect": "Allow",
                  "Sid": ""
                }
              ]
            },
            "RoleId": "AROAJ52OTH4H7LEXAMPLE",
            "CreateDate": "2013-05-11T00:02:27Z",
            "RoleName": "example-role",
            "Path": "/",
            "Arn": "arn:aws:iam::123456789012:role/example-role"
          }
        ],
        "CreateDate": "2013-05-11T00:02:27Z",
        "InstanceProfileName": "ExampleInstanceProfile",
        "Path": "/",
        "Arn": "arn:aws:iam::123456789012:instance-profile/ExampleInstanceProfile"
      },
      {
        "InstanceProfileId": "AIPAJVJVNRIQFREXAMPLE",
        "Roles": [
          {
            "AssumeRolePolicyDocument": {
              "Version": "2012-10-17",
              "Statement": [
                {
                  "Action": "sts:AssumeRole",
                  "Principal": {
                    "Service": "ec2.amazonaws.com"
                  },
                  "Effect": "Allow",
                  "Sid": ""
                }
              ]
            },
            "RoleId": "AROAINUBC5O7XLEXAMPLE",
            "CreateDate": "2013-01-09T06:33:26Z",
            "RoleName": "s3-test-role",
            "Path": "/",
            "Arn": "arn:aws:iam::123456789012:role/s3-test-role"
          }
        ],
        "CreateDate": "2013-06-12T23:52:02Z",
        "InstanceProfileName": "ExampleInstanceProfile2",
        "Path": "/",
        "Arn": "arn:aws:iam::123456789012:instance-profile/ExampleInstanceProfile2"
      },
    ]
  }

For more information, see `Instance Profiles`_ in the *Using IAM* guide.

.. _`Instance Profiles`: http://docs.aws.amazon.com/IAM/latest/UserGuide/instance-profiles.html
