**To get streaming configuration details**

The following ``get-voice-connector-streaming-configuration`` example gets the streaming configuration details for the specified Amazon Chime Voice Connector. ::

    aws chime get-voice-connector-streaming-configuration \
        --voice-connector-id abcdef1ghij2klmno3pqr4

Output::

    {
        "StreamingConfiguration": {
            "DataRetentionInHours": 24,
            "Disabled": false
        }
    }

For more information, see `Streaming Amazon Chime Voice Connector Data to Kinesis <https://docs.aws.amazon.com/chime/latest/ag/start-kinesis-vc.html>`__ in the *Amazon Chime Administration Guide*.
