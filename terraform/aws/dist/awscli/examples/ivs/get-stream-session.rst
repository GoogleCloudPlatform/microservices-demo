**To get metadata for a specified stream**

The following ``get-stream-session`` example gets the metadata configuration for the specified channel ARN (Amazon Resource Name) and the specified stream; if streamId is not provided, the most recent stream for the channel is selected. ::

    aws ivs get-stream-session \
        --channel-arn arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh \
        --stream-id "mystream"

Output::

    {
        "streamSession": {
            "channel": {
                "arn": "arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh",
                "authorized": true,
                "ingestEndpoint": "a1b2c3d4e5f6.global-contribute.live-video.net",
                "insecureIngest": false,
                "latencyMode": "LOW",
                "name": "mychannel",
                "preset": "",
                "playbackUrl": "url-string",
                "recordingConfigurationArn": "arn:aws:ivs:us-west-2:123456789012:recording-configuration/ABcdef34ghIJ",
                "tags": {
                    "key1" : "value1",
                    "key2" : "value2"
                },
                "type": "STANDARD"
            },
            "startTime": 1641578182,
            "endTime": 1641579982,
            "ingestConfiguration": {
                "audio": {
                    "channels": 2,
                    "codec": "mp4a.40.2",
                    "sampleRate": 8000,
                    "targetBitrate": 46875
                },
                "video": {
                    "avcLevel": "4.2",
                    "avcProfile": "Baseline",
                    "codec": "avc1.42C02A",
                    "encoder": "Lavf58.45.100",
                    "targetBitrate": 8789062,
                    "targetFrameRate": 60,
                    "videoHeight": 1080,
                    "videoWidth": 1920
                }
            },
            "recordingConfiguration": {
                "arn": "arn:aws:ivs:us-west-2:123456789012:recording-configuration/ABcdef34ghIJ",
                "destinationConfiguration": {
                    "s3": {
                       "bucketName": "demo-recording-bucket"
                    }
                },
                "name": "test-recording-config",
                "state": "ACTIVE",
                "tags": {
                    "rkey1" : "rvalue1"
                },
                "thumbnailConfiguration": {
                    "recordingMode": "INTERVAL",
                    "targetIntervalSeconds": 30
                }
            },

            "streamId": "mystream1",
            "truncatedEvents": [
                {
                    "eventTime": 1641579941,
                    "name": "Session Ended",
                    "type": "IVS Stream State Change"
                }
            ]
        }
    }

For more information, see `Create a Channel <https://docs.aws.amazon.com/ivs/latest/userguide/GSIVS-create-channel.html>`__ in the *Amazon Interactive Video Service User Guide*.