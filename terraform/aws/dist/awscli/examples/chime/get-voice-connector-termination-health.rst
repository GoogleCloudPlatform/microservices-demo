**To retrieve termination health details**

The following ``get-voice-connector-termination-health`` example retrieves the termination health details for the specified Amazon Chime Voice Connector. ::

    aws chime get-voice-connector-termination-health \
        --voice-connector-id abcdef1ghij2klmno3pqr4

Output::

    {
        "TerminationHealth": {
            "Timestamp": "Fri Aug 23 16:45:55 UTC 2019", 
            "Source": "10.24.34.0"
        }
    }

For more information, see `Working with Amazon Chime Voice Connectors <https://docs.aws.amazon.com/chime/latest/ag/voice-connectors.html>`__ in the *Amazon Chime Administration Guide*.
