**To list all inline policies that are attached to the specified group**

The following ``list-group-policies`` command lists the names of inline policies that are attached to the IAM group named
``Admins`` in the current account::

  aws iam list-group-policies --group-name Admins

Output::

  {
      "PolicyNames": [
          "AdminRoot",
          "ExamplePolicy"
      ]
  }

For more information, see `Managing IAM Policies`_ in the *Using IAM* guide.

.. _`Managing IAM Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/ManagingPolicies.html

