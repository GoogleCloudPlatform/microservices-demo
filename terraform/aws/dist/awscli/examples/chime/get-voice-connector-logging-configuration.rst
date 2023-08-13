**To get logging configuration details**

The following ``get-voice-connector-logging-configuration`` example retreives the logging configuration details for the specified Amazon Chime Voice Connector. ::

    aws chime get-voice-connector-logging-configuration \
        --voice-connector-id abcdef1ghij2klmno3pqr4

Output::

    {
        "LoggingConfiguration": {
            "EnableSIPLogs": true
        }
    }


For more information, see `Streaming Amazon Chime Voice Connector Media to Kinesis <https://docs.aws.amazon.com/chime/latest/ag/start-kinesis-vc.html>`__ in the *Amazon Chime Administration Guide*.