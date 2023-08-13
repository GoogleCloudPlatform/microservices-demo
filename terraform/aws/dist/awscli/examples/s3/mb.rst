The following ``mb`` command creates a bucket.  In this example, the user makes the bucket ``mybucket``.  The bucket is
created in the region specified in the user's configuration file::

    aws s3 mb s3://mybucket

Output::

    make_bucket: s3://mybucket

The following ``mb`` command creates a bucket in a region specified by the ``--region`` parameter.  In this example, the
user makes the bucket ``mybucket`` in the region ``us-west-1``::

    aws s3 mb s3://mybucket --region us-west-1

Output::

    make_bucket: s3://mybucket
