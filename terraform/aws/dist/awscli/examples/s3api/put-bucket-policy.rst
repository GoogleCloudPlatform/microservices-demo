This example allows all users to retrieve any object in *MyBucket* except those in the *MySecretFolder*. It also
grants ``put`` and ``delete`` permission to the root user of the AWS account ``1234-5678-9012``::

   aws s3api put-bucket-policy --bucket MyBucket --policy file://policy.json

   policy.json:
   {
      "Statement": [
         {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::MyBucket/*"
         },
         {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::MyBucket/MySecretFolder/*"
         },
         {
            "Effect": "Allow",
            "Principal": {
               "AWS": "arn:aws:iam::123456789012:root"
            },
            "Action": [
               "s3:DeleteObject",
               "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::MyBucket/*"
         }
      ]
   }

