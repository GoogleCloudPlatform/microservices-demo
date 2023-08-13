**To list IAM roles for the current account**

The following ``list-roles`` command lists IAM roles for the current account::

  aws iam list-roles

Output::

  {
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
        "RoleName": "ExampleRole1",
        "Path": "/",
        "Arn": "arn:aws:iam::123456789012:role/ExampleRole1"
      },
      {
        "AssumeRolePolicyDocument": {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Action": "sts:AssumeRole",
              "Principal": {
                "Service": "elastictranscoder.amazonaws.com"
              },
              "Effect": "Allow",
              "Sid": ""
            }
          ]
        },
        "RoleId": "AROAI4QRP7UFT7EXAMPLE",
        "CreateDate": "2013-04-18T05:01:58Z",
        "RoleName": "emr-access",
        "Path": "/",
        "Arn": "arn:aws:iam::123456789012:role/emr-access"
      }
    ]
  }

For more information, see `Creating a Role`_ in the *Using IAM* guide.

.. _`Creating a Role`: http://docs.aws.amazon.com/IAM/latest/UserGuide/creating-role.html

