The following command retrieves the replication configuration for a bucket named ``my-bucket``::

  aws s3api get-bucket-replication --bucket my-bucket

Output::

  {
      "ReplicationConfiguration": {
          "Rules": [
              {
                  "Status": "Enabled",
                  "Prefix": "",
                  "Destination": {
                      "Bucket": "arn:aws:s3:::my-bucket-backup",
                      "StorageClass": "STANDARD"
                  },
                  "ID": "ZmUwNzE4ZmQ4tMjVhOS00MTlkLOGI4NDkzZTIWJjNTUtYTA1"
              }
          ],
          "Role": "arn:aws:iam::123456789012:role/s3-replication-role"
      }
  }