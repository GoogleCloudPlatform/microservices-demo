The following command retrieves the notification configuration for a bucket named ``my-bucket``::

  aws s3api get-bucket-notification-configuration --bucket my-bucket

Output::

  {
      "TopicConfigurations": [
          {
              "Id": "YmQzMmEwM2EjZWVlI0NGItNzVtZjI1MC00ZjgyLWZDBiZWNl",
              "TopicArn": "arn:aws:sns:us-west-2:123456789012:my-notification-topic",
              "Events": [
                  "s3:ObjectCreated:*"
              ]
          }
      ]
  }
