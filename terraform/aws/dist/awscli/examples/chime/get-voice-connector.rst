**To get details for an Amazon Chime Voice Connector**

The following ``get-voice-connector`` example displays the details of the specified Amazon Chime Voice Connector. ::

    aws chime get-voice-connector \
        --voice-connector-id abcdef1ghij2klmno3pqr4

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
