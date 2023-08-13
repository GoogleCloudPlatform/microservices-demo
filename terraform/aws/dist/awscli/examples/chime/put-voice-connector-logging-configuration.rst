**To add a logging configuration for an Amazon Chime Voice Connector**

The following ``put-voice-connector-logging-configuration`` example turns on the SIP logging configuration for the specified Amazon Chime Voice Connector. ::

    aws chime put-voice-connector-logging-configuration \
        --voice-connector-id abcdef1ghij2klmno3pqr4 \
        --logging-configuration EnableSIPLogs=true

Output::

    {
        "LoggingConfiguration": {
            "EnableSIPLogs": true
        }
    }

For more information, see `Streaming Amazon Chime Voice Connector Media to Kinesis <https://docs.aws.amazon.com/chime/latest/ag/start-kinesis-vc.html>`__ in the *Amazon Chime Administration Guide*.
