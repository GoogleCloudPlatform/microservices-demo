**To list all managed policies that are attached to the specified user**

This command returns the names and ARNs of the managed policies for the IAM user named ``Bob`` in the AWS account::

  aws iam list-attached-user-policies --user-name Bob

Output::

  {
    "AttachedPolicies": [
      {
        "PolicyName": "AdministratorAccess",
        "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
      },
      {
        "PolicyName": "SecurityAudit",
        "PolicyArn": "arn:aws:iam::aws:policy/SecurityAudit"
      }
    ],
    "IsTruncated": false
  }

For more information, see `Overview of IAM Policies`_ in the *Using IAM* guide.

.. _`Overview of IAM Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/policies_overview.html