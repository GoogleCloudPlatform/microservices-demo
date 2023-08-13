**To add a policy to a group**

The following ``put-group-policy`` command adds a policy to the IAM group named ``Admins``::

  aws iam put-group-policy --group-name Admins --policy-document file://AdminPolicy.json --policy-name AdminRoot

The policy is defined as a JSON document in the *AdminPolicy.json* file. (The file name and extension do not have
significance.)

For more information, see `Managing IAM Policies`_ in the *Using IAM* guide.

.. _`Managing IAM Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/ManagingPolicies.html

