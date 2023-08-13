**To delete a version of a managed policy**

This example deletes the version identified as ``v2`` from the policy whose ARN is ``arn:aws:iam::123456789012:policy/MySamplePolicy``::

  aws iam delete-policy-version --policy-arn arn:aws:iam::123456789012:policy/MyPolicy --version-id v2


For more information, see `Overview of IAM Policies`_ in the *Using IAM* guide.

.. _`Overview of IAM Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/policies_overview.html