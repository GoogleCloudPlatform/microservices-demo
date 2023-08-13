**To add a client ID (audience) to an Open-ID Connect (OIDC) provider**

The following ``add-client-id-to-open-id-connect-provider`` command adds the client ID ``my-application-ID`` to the OIDC provider named ``server.example.com``::

  aws iam add-client-id-to-open-id-connect-provider --client-id my-application-ID --open-id-connect-provider-arn arn:aws:iam::123456789012:oidc-provider/server.example.com

To create an OIDC provider, use the ``create-open-id-connect-provider`` command.

For more information, see `Using OpenID Connect Identity Providers`_ in the *Using IAM* guide.

.. _`Using OpenID Connect Identity Providers`: http://docs.aws.amazon.com/IAM/latest/UserGuide/identity-providers-oidc.html