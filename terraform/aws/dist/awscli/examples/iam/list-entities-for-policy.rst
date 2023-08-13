**To list all users, groups, and roles that the specified managed policy is attached to**

This example returns a list of IAM groups, roles, and users who have the policy ``arn:aws:iam::123456789012:policy/TestPolicy`` attached::

  aws iam list-entities-for-policy --policy-arn arn:aws:iam::123456789012:policy/TestPolicy 

Output::

  {
    "PolicyGroups": [
      {
        "GroupName": "Admins"
      }
    ],
    "PolicyUsers": [
      {
        "UserName": "Bob"
      }
    ],
    "PolicyRoles": [
      {
        "RoleName": "testRole"
      }
    ],
    "IsTruncated": false
  }

For more information, see `Overview of IAM Policies`_ in the *Using IAM* guide.

.. _`Overview of IAM Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/policies_overview.html