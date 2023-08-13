**To attach a managed policy to an IAM group**

The following ``attach-group-policy`` command attaches the AWS managed policy named ``ReadOnlyAccess`` to the IAM group named ``Finance``::

  aws iam attach-group-policy --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess --group-name Finance

For more information, see `Managed Policies and Inline Policies`_ in the *Using IAM* guide.

.. _`Managed Policies and Inline Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/policies-managed-vs-inline.html