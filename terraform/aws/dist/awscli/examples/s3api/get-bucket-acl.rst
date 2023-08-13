The following command retrieves the access control list for a bucket named ``my-bucket``::

  aws s3api get-bucket-acl --bucket my-bucket

Output::

  {
      "Owner": {
          "DisplayName": "my-username",
          "ID": "7009a8971cd538e11f6b6606438875e7c86c5b672f46db45460ddcd087d36c32"
      },
      "Grants": [
          {
              "Grantee": {
                  "DisplayName": "my-username",
                  "ID": "7009a8971cd538e11f6b6606438875e7c86c5b672f46db45460ddcd087d36c32"
              },
              "Permission": "FULL_CONTROL"
          }
      ]
  }
