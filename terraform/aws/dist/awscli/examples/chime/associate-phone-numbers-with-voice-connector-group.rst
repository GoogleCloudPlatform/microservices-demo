**To associate phone numbers with an Amazon Chime Voice Connector group**

The following ``associate-phone-numbers-with-voice-connector-group`` example associates the specified phone numbers with an Amazon Chime Voice Connector group. ::

    aws chime associate-phone-numbers-with-voice-connector-group \
        --voice-connector-group-id 123a456b-c7d8-90e1-fg23-4h567jkl8901 \
        --e164-phone-numbers "+12065550100" "+12065550101" \
        --force-associate

Output::

    {
        "PhoneNumberErrors": []
    }

For more information, see `Working with Amazon Chime Voice Connector groups <https://docs.aws.amazon.com/chime/latest/ag/voice-connector-groups.html>`__ in the *Amazon Chime Administration Guide*.
