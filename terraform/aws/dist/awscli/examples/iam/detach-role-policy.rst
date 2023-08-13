**To detach a policy from a role**

This example removes the managed policy with the ARN ``arn:aws:iam::123456789012:policy/FederatedTesterAccessPolicy`` from the role called ``FedTesterRole``::

  aws iam detach-role-policy --role-name FedTesterRole --policy-arn arn:aws:iam::123456789012:policy/FederatedTesterAccessPolicy 


For more information, see `Overview of IAM Policies`_ in the *Using IAM* guide.

.. _`Overview of IAM Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/policies_overview.html