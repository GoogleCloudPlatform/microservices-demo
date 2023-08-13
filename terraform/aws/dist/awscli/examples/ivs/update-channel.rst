**Example 1: To update a channel's configuration information**

The following ``update-channel`` example updates the channel configuration for a specified channel ARN to change the channel name. This does not affect an ongoing stream of this channel; you must stop and restart the stream for the changes to take effect. ::

    aws ivs update-channel \
        --arn arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh \
        --name "channel-1" \
        --insecure-ingest

Output::

    {
        "channel": {
            "arn": "arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh",
            "name": "channel-1",
            "latencyMode": "LOW",
            "type": "STANDARD",
            "recordingConfigurationArn": "",
            "ingestEndpoint": "a1b2c3d4e5f6.global-contribute.live-video.net",
            "insecureIngest": true,
            "playbackUrl": "https://a1b2c3d4e5f6.us-west-2.playback.live-video.net/api/video/v1/us-west-2.123456789012.channel.abcdEFGH.m3u8",
            "preset": "",
            "authorized": false,
            "tags": {}
    }

For more information, see `Create a Channel <https://docs.aws.amazon.com/ivs/latest/userguide/GSIVS-create-channel.html>`__ in the *Amazon Interactive Video Service User Guide*.

**Example 2: To update a channel's configuration to enable recording**

The following ``update-channel`` example updates the channel configuration for a specified channel ARN to enable recording. This does not affect an ongoing stream of this channel; you must stop and restart the stream for the changes to take effect. ::

    aws ivs update-channel \
        --arn "arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh" \
        --no-insecure-ingest \
        --recording-configuration-arn "arn:aws:ivs:us-west-2:123456789012:recording-configuration/ABCD12cdEFgh"

Output::

    {
        "channel": {
            "arn": "arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh",
            "name": "test-channel-with-recording",
            "latencyMode": "LOW",
            "type": "STANDARD",
            "recordingConfigurationArn": "arn:aws:ivs:us-west-2:123456789012:recording-configuration/ABCD12cdEFgh",
            "ingestEndpoint": "a1b2c3d4e5f6.global-contribute.live-video.net",
            "insecureIngest": false,
            "playbackUrl": "https://a1b2c3d4e5f6.us-west-2.playback.live-video.net/api/video/v1/us-west-2.123456789012.channel.abcdEFGH.m3u8",
            "preset": "",
            "authorized": false,
            "tags": {}
        }
    }

For more information, see `Record to Amazon S3 <https://docs.aws.amazon.com/ivs/latest/userguide/record-to-s3.html>`__ in the *Amazon Interactive Video Service User Guide*.

**Example 3: To update a channel's configuration to disable recording**

The following ``update-channel`` example updates the channel configuration for a specified channel ARN to disable recording. This does not affect an ongoing stream of this channel; you must stop and restart the stream for the changes to take effect. ::

    aws ivs update-channel \
        --arn "arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh" \
        --recording-configuration-arn ""

Output::

    {
        "channel": {
            "arn": "arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh",
            "name": "test-channel-with-recording",
            "latencyMode": "LOW",
            "type": "STANDARD",
            "recordingConfigurationArn": "",
            "ingestEndpoint": "a1b2c3d4e5f6.global-contribute.live-video.net",
            "insecureIngest": false,
            "playbackUrl": "https://a1b2c3d4e5f6.us-west-2.playback.live-video.net/api/video/v1/us-west-2.123456789012.channel.abcdEFGH.m3u8",
            "preset": "",
            "authorized": false,
            "tags": {}
        }
    }

For more information, see `Record to Amazon S3 <https://docs.aws.amazon.com/ivs/latest/userguide/record-to-s3.html>`__ in the *Amazon Interactive Video Service User Guide*.