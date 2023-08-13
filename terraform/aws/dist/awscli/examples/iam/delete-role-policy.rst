**To remove a policy from an IAM role**

The following ``delete-role-policy`` command removes the policy named ``ExamplePolicy`` from the role named ``Test-Role``::

  aws iam delete-role-policy --role-name Test-Role --policy-name ExamplePolicy

For more information, see `Creating a Role`_ in the *Using IAM* guide.

.. _`Creating a Role`: http://docs.aws.amazon.com/IAM/latest/UserGuide/creating-role.html

