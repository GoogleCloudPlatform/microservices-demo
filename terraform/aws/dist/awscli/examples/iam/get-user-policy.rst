**To list policy details for an IAM user**

The following ``get-user-policy`` command lists the details of the specified policy that is attached to the IAM user named ``Bob``::

  aws iam get-user-policy --user-name Bob --policy-name ExamplePolicy

Output::

  {
      "UserName": "Bob",
      "PolicyName": "ExamplePolicy",
      "PolicyDocument": {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Action": "*",
                  "Resource": "*",
                  "Effect": "Allow"
              }
          ]
      }
  }

To get a list of policies for an IAM user, use the ``list-user-policies`` command.

For more information, see `Adding a New User to Your AWS Account`_ in the *Using IAM* guide.

.. _`Adding a New User to Your AWS Account`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_SettingUpUser.html





