**To create a SAML provider**

This example creates a new SAML provider in IAM named ``MySAMLProvider``. It is described by the SAML metadata document found in the file ``SAMLMetaData.xml``::

  aws iam create-saml-provider --saml-metadata-document file://SAMLMetaData.xml --name MySAMLProvider


Output::

  {
      "SAMLProviderArn": "arn:aws:iam::123456789012:saml-provider/MySAMLProvider"
  }

For more information, see `Using SAML Providers`_ in the *Using IAM* guide.

.. _`Using SAML Providers`: http://docs.aws.amazon.com/IAM/latest/UserGuide/identity-providers-saml.html