**To delete a SAML provider**

This example deletes the IAM SAML 2.0 provider whose ARN is ``arn:aws:iam::123456789012:saml-provider/SAMLADFSProvider``::

  aws iam delete-saml-provider --saml-provider-arn arn:aws:iam::123456789012:saml-provider/SAMLADFSProvider


For more information, see `Using SAML Providers`_ in the *Using IAM* guide.

.. _`Using SAML Providers`: http://docs.aws.amazon.com/IAM/latest/UserGuide/identity-providers-saml.html