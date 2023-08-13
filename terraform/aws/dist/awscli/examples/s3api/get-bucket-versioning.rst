The following command retrieves the versioning configuration for a bucket named ``my-bucket``::

  aws s3api get-bucket-versioning --bucket my-bucket

Output::

  {
      "Status": "Enabled"
  }
