**To get information about an IAM user**

The following ``get-user`` command gets information about the IAM user named ``Paulo``::

  aws iam get-user --user-name Paulo

Output::

  {
      "User": {
          "UserName": "Paulo",
          "Path": "/",
          "CreateDate": "2019-09-21T23:03:13Z",
          "UserId": "AIDA123456789EXAMPLE",
          "Arn": "arn:aws:iam::123456789012:user/Paulo"
      }
  }

For more information, see `Listing Users`_ in the *Using IAM* guide.

.. _`Listing Users`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_GetListOfUsers.html


