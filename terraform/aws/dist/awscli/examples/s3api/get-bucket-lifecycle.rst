The following command retrieves the lifecycle configuration for a bucket named ``my-bucket``::

  aws s3api get-bucket-lifecycle --bucket my-bucket

Output::

  {
    "Rules": [
      {
        "ID": "Move to Glacier after sixty days (objects in logs/2015/)",
        "Prefix": "logs/2015/",
        "Status": "Enabled",
        "Transition": {
          "Days": 60,
          "StorageClass": "GLACIER"
        }
      },
      {
        "Expiration": {
          "Date": "2016-01-01T00:00:00.000Z"
        },
        "ID": "Delete 2014 logs in 2016.",
        "Prefix": "logs/2014/",
        "Status": "Enabled"
      }
    ]
  }
