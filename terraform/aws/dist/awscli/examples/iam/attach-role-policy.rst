**To attach a managed policy to an IAM role**

The following ``attach-role-policy`` command attaches the AWS managed policy named ``ReadOnlyAccess`` to the IAM role named ``ReadOnlyRole``::

  aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess --role-name ReadOnlyRole

For more information, see `Managed Policies and Inline Policies`_ in the *Using IAM* guide.

.. _`Managed Policies and Inline Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/policies-managed-vs-inline.html