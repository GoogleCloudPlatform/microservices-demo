**To detach a policy from a user**

This example removes the managed policy with the ARN ``arn:aws:iam::123456789012:policy/TesterPolicy`` from the user ``Bob``::

  aws iam detach-user-policy --user-name Bob --policy-arn arn:aws:iam::123456789012:policy/TesterPolicy 


For more information, see `Overview of IAM Policies`_ in the *Using IAM* guide.

.. _`Overview of IAM Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/policies_overview.html