The following command retrieves the location constraint for a bucket named ``my-bucket``, if a constraint exists::

  aws s3api get-bucket-location --bucket my-bucket

Output::

  {
      "LocationConstraint": "us-west-2"
  }