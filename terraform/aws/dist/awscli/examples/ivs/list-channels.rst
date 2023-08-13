**Example 1: To get summary information about all channels**

The following ``list-channels`` example lists all channels for your AWS account. ::

    aws ivs list-channels

Output::

    {
        "channels": [
            {
                "arn": "arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh",
                "name": "channel-1",
                "latencyMode": "LOW",
                "authorized": false,
                "insecureIngest": false,
                "preset": "",
                "recordingConfigurationArn": "arn:aws:ivs:us-west-2:123456789012:recording-configuration/ABCD12cdEFgh",
                "tags": {},
                "type": "STANDARD"
            },
            {
                "arn": "arn:aws:ivs:us-west-2:123456789012:channel/efghEFGHijkl",
                "name": "channel-2",
                "latencyMode": "LOW",
                "authorized": false,
                "preset": "",
                "recordingConfigurationArn": "",
                "tags": {},
                "type": "STANDARD"
            }
        ]
    }

For more information, see `Create a Channel <https://docs.aws.amazon.com/ivs/latest/userguide/GSIVS-create-channel.html>`__ in the *Amazon Interactive Video Service User Guide*.

**Example 2: To get summary information about all channels, filtered by the specified RecordingConfiguration ARN**

The following ``list-channels`` example lists all channels for your AWS account, that are associated with the specified RecordingConfiguration ARN. ::

    aws ivs list-channels \
        --filter-by-recording-configuration-arn "arn:aws:ivs:us-west-2:123456789012:recording-configuration/ABCD12cdEFgh"

Output::

    {
        "channels": [
            {
                "arn": "arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh",
                "name": "channel-1",
                "latencyMode": "LOW",
                "authorized": false,
                "insecureIngest": false,
                "preset": "",
                "recordingConfigurationArn": "arn:aws:ivs:us-west-2:123456789012:recording-configuration/ABCD12cdEFgh",
                "tags": {},
                "type": "STANDARD"
            }
        ]
    }

For more information, see `Record to Amazon S3 <https://docs.aws.amazon.com/ivs/latest/userguide/record-to-s3.html>`__ in the *Amazon Interactive Video Service User Guide*.