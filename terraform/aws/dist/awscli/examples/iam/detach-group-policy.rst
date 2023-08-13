**To detach a policy from a group**

This example removes the managed policy with the ARN ``arn:aws:iam::123456789012:policy/TesterAccessPolicy`` from the group called ``Testers``::

  aws iam detach-group-policy --group-name Testers --policy-arn arn:aws:iam::123456789012:policy/TesterAccessPolicy


For more information, see `Overview of IAM Policies`_ in the *Using IAM* guide.

.. _`Overview of IAM Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/policies_overview.html