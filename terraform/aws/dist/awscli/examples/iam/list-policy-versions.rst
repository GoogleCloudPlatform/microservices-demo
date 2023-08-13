**To list information about the versions of the specified managed policy**

This example returns the list of available versions of the policy whose ARN is ``arn:aws:iam::123456789012:policy/MySamplePolicy``::

  aws iam list-policy-versions --policy-arn arn:aws:iam::123456789012:policy/MySamplePolicy 

Output::

  {
    "IsTruncated": false,
    "Versions": [
      {
        "CreateDate": "2015-06-02T23:19:44Z",
        "VersionId": "v2",
        "IsDefaultVersion": true
      },
      {
        "CreateDate": "2015-06-02T22:30:47Z",
        "VersionId": "v1",
        "IsDefaultVersion": false
      }
    ]
  }

For more information, see `Overview of IAM Policies`_ in the *Using IAM* guide.

.. _`Overview of IAM Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/policies_overview.html