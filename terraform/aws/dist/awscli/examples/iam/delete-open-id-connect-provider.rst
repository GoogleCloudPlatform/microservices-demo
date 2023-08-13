**To delete an IAM OpenID Connect identity provider**

This example deletes the IAM OIDC provider that connects to the provider ``example.oidcprovider.com``::

  aws iam delete-open-id-connect-provider --open-id-connect-provider-arn arn:aws:iam::123456789012:oidc-provider/example.oidcprovider.com


For more information, see `Using OpenID Connect Identity Providers`_ in the *Using IAM* guide.

.. _`Using OpenID Connect Identity Providers`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_CreatingAndListingGroups.html