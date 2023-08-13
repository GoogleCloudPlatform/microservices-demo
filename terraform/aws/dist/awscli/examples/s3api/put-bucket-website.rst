The applies a static website configuration to a bucket named ``my-bucket``::

  aws s3api put-bucket-website --bucket my-bucket --website-configuration file://website.json

The file ``website.json`` is a JSON document in the current folder that specifies index and error pages for the website::

  {
      "IndexDocument": {
          "Suffix": "index.html"
      },
      "ErrorDocument": {
          "Key": "error.html"
      }
  }
