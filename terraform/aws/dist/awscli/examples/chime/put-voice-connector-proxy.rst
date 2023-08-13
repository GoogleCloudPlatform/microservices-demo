**To put a proxy configuration**

The following ``put-voice-connector-proxy`` example sets a proxy configuration to your Amazon Chime Voice Connector. ::

    aws chime put-voice-connector-proxy \
        --voice-connector-id abcdef1ghij2klmno3pqr4 \
        --default-session-expiry-minutes 60 \
        --phone-number-pool-countries "US"

Output::

    {
        "Proxy": {
            "DefaultSessionExpiryMinutes": 60,
            "Disabled": false,
            "PhoneNumberCountries": [
                "US"
            ]
        }
    }

For more information, see `Proxy Phone Sessions <https://docs.aws.amazon.com/chime/latest/dg/proxy-phone-sessions.html>`__ in the *Amazon Chime Developer Guide*.
