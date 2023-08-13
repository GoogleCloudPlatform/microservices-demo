**To retrieve the SAML provider metadocument**

This example retrieves the details about the SAML 2.0 provider whose ARM is ``arn:aws:iam::123456789012:saml-provider/SAMLADFS``. 
The response includes the metadata document that you got from the identity provider to create the AWS SAML provider entity as well 
as the creation and expiration dates::

  aws iam get-saml-provider --saml-provider-arn arn:aws:iam::123456789012:saml-provider/SAMLADFS 


For more information, see `Using SAML Providers`_ in the *Using IAM* guide.

.. _`Using SAML Providers`: http://docs.aws.amazon.com/IAM/latest/UserGuide/identity-providers-saml.html