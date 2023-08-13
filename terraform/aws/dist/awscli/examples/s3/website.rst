The following command configures a bucket named ``my-bucket`` as a static website::

  aws s3 website s3://my-bucket/ --index-document index.html --error-document error.html

The index document option specifies the file in ``my-bucket`` that visitors will be directed to when they navigate to the website URL. In this case, the bucket is in the us-west-2 region, so the site would appear at ``http://my-bucket.s3-website-us-west-2.amazonaws.com``. 

All files in the bucket that appear on the static site must be configured to allow visitors to open them. File permissions are configured separately from the bucket website configuration. For information on hosting a static website in Amazon S3, see `Hosting a Static Website`_ in the *Amazon Simple Storage Service Developer Guide*.

.. _`Hosting a Static Website`: http://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html