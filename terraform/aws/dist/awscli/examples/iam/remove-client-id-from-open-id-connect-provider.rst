**To remove the specified client ID from the list of client IDs registered for the specified IAM OpenID Connect provider**

This example removes the client ID ``My-TestApp-3`` from the list of client IDs associated with the IAM OIDC provider whose 
ARN is ``arn:aws:iam::123456789012:oidc-provider/example.oidcprovider.com``::

  aws iam remove-client-id-from-open-id-connect-provider --client-id My-TestApp-3 --open-id-connect-provider-arn arn:aws:iam::123456789012:oidc-provider/example.oidcprovider.com


For more information, see `Using OpenID Connect Identity Providers`_ in the *Using IAM* guide.

.. _`Using OpenID Connect Identity Providers`: http://docs.aws.amazon.com/IAM/latest/UserGuide/identity-providers-oidc.html