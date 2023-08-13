**To get proxy configuration details**

The following ``get-voice-connector-proxy`` example gets the proxy configuration details for your Amazon Chime Voice Connector. ::

    aws chime get-voice-connector-proxy \
        --voice-connector-id abcdef1ghij2klmno3pqr4

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
