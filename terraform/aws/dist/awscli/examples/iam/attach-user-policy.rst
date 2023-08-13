**To attach a managed policy to an IAM user**

The following ``attach-user-policy`` command attaches the AWS managed policy named ``AdministratorAccess`` to the IAM user named ``Alice``::

  aws iam attach-user-policy --policy-arn arn:aws:iam:ACCOUNT-ID:aws:policy/AdministratorAccess --user-name Alice

For more information, see `Managed Policies and Inline Policies`_ in the *Using IAM* guide.

.. _`Managed Policies and Inline Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/policies-managed-vs-inline.html
