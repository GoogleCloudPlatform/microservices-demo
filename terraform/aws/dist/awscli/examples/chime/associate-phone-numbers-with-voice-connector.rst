**To associate phone numbers with an Amazon Chime Voice Connector**

The following ``associate-phone-numbers-with-voice-connector`` example  associates the specified phone numbers with an Amazon Chime Voice Connector. ::

    aws chime associate-phone-numbers-with-voice-connector \
        --voice-connector-id abcdef1ghij2klmno3pqr4 \
        --e164-phone-numbers "+12065550100" "+12065550101"
        --force-associate

Output::

    {
        "PhoneNumberErrors": []
    }

For more information, see `Working with Amazon Chime Voice Connectors <https://docs.aws.amazon.com/chime/latest/ag/voice-connectors.html>`__ in the *Amazon Chime Administration Guide*.
