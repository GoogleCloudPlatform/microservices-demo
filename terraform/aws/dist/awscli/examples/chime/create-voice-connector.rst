**To create an Amazon Chime Voice Connector**

The following ``create-voice-connector`` example creates an Amazon Chime Voice Connector in the specified AWS Region, with encryption enabled. ::

    aws chime create-voice-connector \
        --name newVoiceConnector \
        --aws-region us-west-2 \
        --require-encryption

Output::

    {
        "VoiceConnector": {
            "VoiceConnectorId": "abcdef1ghij2klmno3pqr4",
            "AwsRegion": "us-west-2",
            "Name": "newVoiceConnector",
            "OutboundHostName": "abcdef1ghij2klmno3pqr4.voiceconnector.chime.aws",
            "RequireEncryption": true,
            "CreatedTimestamp": "2019-09-18T20:34:01.352Z",
            "UpdatedTimestamp": "2019-09-18T20:34:01.352Z"
        }
    }

For more information, see `Working with Amazon Chime Voice Connectors <https://docs.aws.amazon.com/chime/latest/ag/voice-connectors.html>`__ in the *Amazon Chime Administration Guide*.
