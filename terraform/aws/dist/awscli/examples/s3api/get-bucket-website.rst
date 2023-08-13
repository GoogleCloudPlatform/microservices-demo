The following command retrieves the static website configuration for a bucket named ``my-bucket``::

  aws s3api get-bucket-website --bucket my-bucket

Output::

  {
      "IndexDocument": {
          "Suffix": "index.html"
      },
      "ErrorDocument": {
          "Key": "error.html"
      }
  }
