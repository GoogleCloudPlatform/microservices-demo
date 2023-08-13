**To retrieve information about when the specified access key was last used**

The following example retrieves information about when the access key ``ABCDEXAMPLE`` was last used::

  aws iam get-access-key-last-used --access-key-id ABCDEXAMPLE


Output::

  {
    "UserName":  "Bob",
    "AccessKeyLastUsed": {
        "Region": "us-east-1",
        "ServiceName": "iam",
        "LastUsedDate": "2015-06-16T22:45:00Z"
    }
  }

For more information, see `Managing Access Keys for IAM Users`_ in the *Using IAM* guide.

.. _`Managing Access Keys for IAM Users`: http://docs.aws.amazon.com/IAM/latest/UserGuide/ManagingCredentials.html