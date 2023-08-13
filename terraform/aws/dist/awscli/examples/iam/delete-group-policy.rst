**To delete a policy from an IAM group**

The following ``delete-group-policy`` command deletes the policy named ``ExamplePolicy`` from the group named ``Admins``::

  aws iam delete-group-policy --group-name Admins --policy-name ExamplePolicy

To see the policies attached to a group, use the ``list-group-policies`` command.

For more information, see `Managing IAM Policies`_ in the *Using IAM* guide.

.. _`Managing IAM Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/ManagingPolicies.html

