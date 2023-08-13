**To get details for an Amazon Chime Voice Connector group**

The following ``get-voice-connector-group`` example displays details for the specified Amazon Chime Voice Connector group. ::

    aws chime get-voice-connector-group \
        --voice-connector-group-id 123a456b-c7d8-90e1-fg23-4h567jkl8901

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
