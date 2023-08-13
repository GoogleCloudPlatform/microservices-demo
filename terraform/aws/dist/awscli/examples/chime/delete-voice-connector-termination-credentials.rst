**To delete termination credentials**

The following ``delete-voice-connector-termination-credentials`` example deletes the termination credentials for the specified user name and Amazon Chime Voice Connector. ::

    aws chime delete-voice-connector-termination-credentials \
        --voice-connector-id abcdef1ghij2klmno3pqr4 \
        --usernames "jdoe"

This command produces no output.

For more information, see `Working with Amazon Chime Voice Connectors <https://docs.aws.amazon.com/chime/latest/ag/voice-connectors.html>`__ in the *Amazon Chime Administration Guide*.
