**To list Amazon Chime Voice Connectors for an account**

The following ``list-voice-connectors`` example lists the Amazon Chime Voice Connectors associated with the caller's account. ::

    aws chime list-voice-connectors

Output::

    {
        "VoiceConnectors": [
            {
                "VoiceConnectorId": "abcdef1ghij2klmno3pqr4",
                "AwsRegion": "us-east-1",
                "Name": "MyVoiceConnector",
                "OutboundHostName": "abcdef1ghij2klmno3pqr4.voiceconnector.chime.aws",
                "RequireEncryption": true,
                "CreatedTimestamp": "2019-06-04T18:46:56.508Z",
                "UpdatedTimestamp": "2019-09-18T16:33:00.806Z"
            },
            {
                "VoiceConnectorId": "cbadef1ghij2klmno3pqr5",
                "AwsRegion": "us-west-2",
                "Name": "newVoiceConnector",
                "OutboundHostName": "cbadef1ghij2klmno3pqr5.voiceconnector.chime.aws",
                "RequireEncryption": true,
                "CreatedTimestamp": "2019-09-18T20:34:01.352Z",
                "UpdatedTimestamp": "2019-09-18T20:34:01.352Z"
            }
        ]
    }

For more information, see `Working with Amazon Chime Voice Connectors <https://docs.aws.amazon.com/chime/latest/ag/voice-connectors.html>`__ in the *Amazon Chime Administration Guide*.
