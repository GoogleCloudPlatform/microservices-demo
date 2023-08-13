**To set up termination settings**

The following ``put-voice-connector-termination`` example sets the calling regions and allowed IP host termination settings for the specified Amazon Chime Voice Connector. ::

    aws chime put-voice-connector-termination \
        --voice-connector-id abcdef1ghij2klmno3pqr4 \
        --termination CallingRegions="US",CidrAllowedList="10.24.34.0/23",Disabled=false

Output::

    {
        "Termination": {
            "CpsLimit": 0,
            "CallingRegions": [
                "US"
            ],
            "CidrAllowedList": [
                "10.24.34.0/23"
            ],
            "Disabled": false
        }
    }

For more information, see `Working with Amazon Chime Voice Connectors <https://docs.aws.amazon.com/chime/latest/ag/voice-connectors.html>`__ in the *Amazon Chime Administration Guide*.
