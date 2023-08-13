**To set the specified version of the specified policy as the policy's default version.**

This example sets the ``v2`` version of the policy whose ARN is ``arn:aws:iam::123456789012:policy/MyPolicy`` as the default active version::

  aws iam set-default-policy-version --policy-arn arn:aws:iam::123456789012:policy/MyPolicy --version-id v2


For more information, see `Overview of IAM Policies`_ in the *Using IAM* guide.

.. _`Overview of IAM Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/policies_overview.html