**To update the details for an Amazon Chime Voice Connector group**

The following ``update-voice-connector-group`` example updates the details of the specified Amazon Chime Voice Connector group. ::

    aws chime update-voice-connector-group \
        --voice-connector-group-id 123a456b-c7d8-90e1-fg23-4h567jkl8901 \
        --name "newGroupName" \
        --voice-connector-items VoiceConnectorId=abcdef1ghij2klmno3pqr4,Priority=1

Output::

    {
        "VoiceConnectorGroup": {
            "VoiceConnectorGroupId": "123a456b-c7d8-90e1-fg23-4h567jkl8901",
            "Name": "newGroupName",
            "VoiceConnectorItems": [
                {
                    "VoiceConnectorId": "abcdef1ghij2klmno3pqr4",
                    "Priority": 1
                }
            ],
            "CreatedTimestamp": "2019-09-18T16:38:34.734Z",
            "UpdatedTimestamp": "2019-10-28T19:00:57.081Z"
        }
    }

For more information, see `Working with Amazon Chime Voice Connector Groups <https://docs.aws.amazon.com/chime/latest/ag/voice-connector-groups.html>`__ in the *Amazon Chime Administration Guide*.
