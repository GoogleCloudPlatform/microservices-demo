**To disassociate phone numbers from an Amazon Chime Voice Connector**

The following ``disassociate-phone-numbers-from-voice-connector`` example disassociates the specified phone numbers from an Amazon Chime Voice Connector. ::

    aws chime disassociate-phone-numbers-from-voice-connector \
        --voice-connector-id abcdef1ghij2klmno3pqr4 \
        --e164-phone-numbers "+12065550100" "+12065550101"

Output::

    {
        "PhoneNumberErrors": []
    }

For more information, see `Working with Amazon Chime Voice Connectors <https://docs.aws.amazon.com/chime/latest/ag/voice-connectors.html>`__ in the *Amazon Chime Administration Guide*.
