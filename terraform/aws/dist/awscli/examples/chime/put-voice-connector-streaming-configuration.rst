**To create a streaming configuration**

The following ``put-voice-connector-streaming-configuration`` example creates a streaming configuration for the specified Amazon Chime Voice Connector. It enables media streaming from the Amazon Chime Voice Connector to Amazon Kinesis, and sets the data retention period to 24 hours. ::

    aws chime put-voice-connector-streaming-configuration \
        --voice-connector-id abcdef1ghij2klmno3pqr4 \
        --streaming-configuration DataRetentionInHours=24,Disabled=false

Output::

    {
        "StreamingConfiguration": {
            "DataRetentionInHours": 24,
            "Disabled": false
        }
    }

For more information, see `Streaming Amazon Chime Voice Connector Data to Kinesis <https://docs.aws.amazon.com/chime/latest/ag/start-kinesis-vc.html>`__ in the *Amazon Chime Administration Guide*.
