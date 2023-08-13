**To list Amazon Chime Voice Connector groups for an Amazon Chime account**

The following ``list-voice-connector-groups`` example lists the Amazon Chime Voice Connector groups associated with the administrator's Amazon Chime account. ::

    aws chime list-voice-connector-groups

Output::

    {
        "VoiceConnectorGroups": [
            {
                "VoiceConnectorGroupId": "123a456b-c7d8-90e1-fg23-4h567jkl8901",
                "Name": "myGroup",
                "VoiceConnectorItems": [],
                "CreatedTimestamp": "2019-09-18T16:38:34.734Z",
                "UpdatedTimestamp": "2019-09-18T16:38:34.734Z"
            }
        ]
    }

For more information, see `Working with Amazon Chime Voice Connector groups <https://docs.aws.amazon.com/chime/latest/ag/voice-connector-groups.html>`__ in the *Amazon Chime Administration Guide*.
