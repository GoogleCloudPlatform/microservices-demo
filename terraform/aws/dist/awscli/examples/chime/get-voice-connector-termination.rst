**To retrieve termination settings**

The following ``get-voice-connector-termination`` example retrieves the termination settings for the specified Amazon Chime Voice Connector. ::

    aws chime get-voice-connector-termination \
        --voice-connector-id abcdef1ghij2klmno3pqr4

This command produces no output.
Output::

    {
        "Termination": {
            "CpsLimit": 1,
            "DefaultPhoneNumber": "+12065550100",
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
