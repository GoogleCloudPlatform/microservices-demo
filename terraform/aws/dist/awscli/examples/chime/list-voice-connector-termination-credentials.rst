**To retrieve a list of termination credentials**

The following ``list-voice-connector-termination-credentials`` example retrieves a list of the termination credentials for the specified Amazon Chime Voice Connector. ::

    aws chime list-voice-connector-termination-credentials \
        --voice-connector-id abcdef1ghij2klmno3pqr4

This command produces no output.
Output::

    {
        "Usernames": [
            "jdoe"
        ]
    }

For more information, see `Working with Amazon Chime Voice Connectors <https://docs.aws.amazon.com/chime/latest/ag/voice-connectors.html>`__ in the *Amazon Chime Administration Guide*.
