**To set up termination credentials**

The following ``put-voice-connector-termination-credentials`` example sets termination credentials for the specified Amazon Chime Voice Connector. ::

    aws chime put-voice-connector-termination-credentials \
        --voice-connector-id abcdef1ghij2klmno3pqr4 \
        --credentials Username="jdoe",Password="XXXXXXXX"

This command produces no output.

For more information, see `Working with Amazon Chime Voice Connectors <https://docs.aws.amazon.com/chime/latest/ag/voice-connectors.html>`__ in the *Amazon Chime Administration Guide*.
