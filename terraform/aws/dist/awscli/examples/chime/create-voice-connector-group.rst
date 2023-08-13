**To create an Amazon Chime Voice Connector group**

The following ``create-voice-connector-group`` example creates an Amazon Chime Voice Connector group that includes the specified Amazon Chime Voice Connector. ::

    aws chime create-voice-connector-group \
        --name myGroup \
        --voice-connector-items VoiceConnectorId=abcdef1ghij2klmno3pqr4,Priority=2

Output::

    {
        "VoiceConnectorGroup": {
            "VoiceConnectorGroupId": "123a456b-c7d8-90e1-fg23-4h567jkl8901",
            "Name": "myGroup",
            "VoiceConnectorItems": [],
            "CreatedTimestamp": "2019-09-18T16:38:34.734Z",
            "UpdatedTimestamp": "2019-09-18T16:38:34.734Z"
        }
    }

For more information, see `Working with Amazon Chime Voice Connector Groups <https://docs.aws.amazon.com/chime/latest/ag/voice-connector-groups.html>`__ in the *Amazon Chime Administration Guide*.
