**To get channel configuration information about multiple channels**

The following ``batch-get-channel`` example lists information about the specified channels. ::

    aws ivs batch-get-channel \
        --arns arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh \
            arn:aws:ivs:us-west-2:123456789012:channel/efghEFGHijkl

Output::

    {
        "channels": [
            {
                "arn": "arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh",
                "authorized": false,
                "ingestEndpoint": "a1b2c3d4e5f6.global-contribute.live-video.net",
                "insecureIngest": false,
                "latencyMode": "LOW",
                "name": "channel-1",
                "playbackUrl": "https://a1b2c3d4e5f6.us-west-2.playback.live-video.net/api/video/v1/us-west-2.123456789012.channel-1.abcdEFGH.m3u8",
                "preset": "",
                "recordingConfigurationArn": "arn:aws:ivs:us-west-2:123456789012:recording-configuration/ABCD12cdEFgh",
                "tags": {},
                "type": "STANDARD"
            },
            {
                "arn": "arn:aws:ivs:us-west-2:123456789012:channel/efghEFGHijkl",
                "authorized": false,
                "ingestEndpoint": "a1b2c3d4e5f6.global-contribute.live-video.net",
                "insecureIngest": true,
                "latencyMode": "LOW",
                "name": "channel-2",
                "playbackUrl": "https://a1b2c3d4e5f6.us-west-2.playback.live-video.net/api/video/v1/us-west-2.123456789012.channel-2.abcdEFGH.m3u8",
                "preset": "",
                "recordingConfigurationArn": "",
                "tags": {},
                "type": "STANDARD"
            }
        ]
    }

For more information, see `Create a Channel <https://docs.aws.amazon.com/ivs/latest/userguide/GSIVS-create-channel.html>`__ in the *Amazon Interactive Video Service User Guide*.