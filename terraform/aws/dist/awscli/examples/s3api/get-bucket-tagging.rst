The following command retrieves the tagging configuration for a bucket named ``my-bucket``::

  aws s3api get-bucket-tagging --bucket my-bucket

Output::

  {
      "TagSet": [
          {
              "Value": "marketing",
              "Key": "organization"
          }
      ]
  }
