**To list the SAML providers in the AWS account**

This example retrieves the list of SAML 2.0 providers created in the current AWS account::

  aws iam list-saml-providers

Output::

  {
    "SAMLProviderList": [
      {
        "CreateDate": "2015-06-05T22:45:14Z",
        "ValidUntil": "2015-06-05T22:45:14Z",
        "Arn": "arn:aws:iam::123456789012:saml-provider/SAMLADFS"
      }
    ]
  }

For more information, see `Using SAML Providers`_ in the *Using IAM* guide.

.. _`Using SAML Providers`: http://docs.aws.amazon.com/IAM/latest/UserGuide/identity-providers-saml.html