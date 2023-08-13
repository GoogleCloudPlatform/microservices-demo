**To replace the existing list of server certificate thumbprints with a new list**

This example updates the certificate thumbprint list for the OIDC provider whose ARN is 
``arn:aws:iam::123456789012:oidc-provider/example.oidcprovider.com`` to use a new thumbprint::

  aws iam update-open-id-connect-provider-thumbprint --open-id-connect-provider-arn arn:aws:iam::123456789012:oidc-provider/example.oidcprovider.com --thumbprint-list 7359755EXAMPLEabc3060bce3EXAMPLEec4542a3


For more information, see `Using OpenID Connect Identity Providers`_ in the *Using IAM* guide.

.. _`Using OpenID Connect Identity Providers`: http://docs.aws.amazon.com/IAM/latest/UserGuide/identity-providers-oidc.html