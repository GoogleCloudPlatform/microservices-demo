The following command applies a tagging configuration to a bucket named ``my-bucket``::

  aws s3api put-bucket-tagging --bucket my-bucket --tagging file://tagging.json

The file ``tagging.json`` is a JSON document in the current folder that specifies tags::

  {
     "TagSet": [
       {
         "Key": "organization",
         "Value": "marketing"
       }
     ]
  }

Or apply a tagging configuration to ``my-bucket`` directly from the command line::

  aws s3api put-bucket-tagging --bucket my-bucket --tagging 'TagSet=[{Key=organization,Value=marketing}]'
