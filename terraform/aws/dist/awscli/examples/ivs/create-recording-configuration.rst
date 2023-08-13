**To create a RecordingConfiguration resource**

The following ``create-recording-configuration`` example creates a RecordingConfiguration resource to enable recording to Amazon S3. ::

    aws ivs create-recording-configuration \
        --name "test-recording-config" \
        --recording-reconnect-window-seconds 60 \
        --tags "key1=value1, key2=value2" \
        --destination-configuration s3={bucketName=demo-recording-bucket} \
        --thumbnail-configuration recordingMode="INTERVAL",targetIntervalSeconds=30

Output::

    {
        "recordingConfiguration": {
            "arn": "arn:aws:ivs:us-west-2:123456789012:recording-configuration/ABcdef34ghIJ",
            "destinationConfiguration": {
                "s3": {
                    "bucketName": "demo-recording-bucket"
                }
            },
            "name": "test-recording-config",
            "recordingReconnectWindowSeconds": 60,
            "state": "CREATING",
            "tags": { "key1" : "value1" },
            "thumbnailConfiguration": { 
                "recordingMode": "INTERVAL",
                "targetIntervalSeconds": 30
            }
        }
    }

For more information, see `Record to Amazon S3 <https://docs.aws.amazon.com/ivs/latest/userguide/record-to-s3.html>`__ in the *Amazon Interactive Video Service User Guide*.