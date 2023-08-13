**To update a proxy session**

The following ``update-proxy-session`` example updates the proxy session capabilities. ::

    aws chime update-proxy-session \
        --voice-connector-id abcdef1ghij2klmno3pqr4 \
        --proxy-session-id 123a4bc5-67d8-901e-2f3g-h4ghjk56789l \
        --capabilities "Voice"

Output::

    {
        "ProxySession": {
            "VoiceConnectorId": "abcdef1ghij2klmno3pqr4",
            "ProxySessionId": "123a4bc5-67d8-901e-2f3g-h4ghjk56789l",
            "Status": "Open",
            "ExpiryMinutes": 60,
            "Capabilities": [
                "Voice"
            ],
            "CreatedTimestamp": "2020-04-15T16:10:10.288Z",
            "UpdatedTimestamp": "2020-04-15T16:10:10.288Z",
            "Participants": [
                {
                    "PhoneNumber": "+12065550100",
                    "ProxyPhoneNumber": "+19135550199"
                },
                {
                    "PhoneNumber": "+14015550101",
                    "ProxyPhoneNumber": "+19135550199"
                }
            ]
        }
    }

For more information, see `Proxy Phone Sessions <https://docs.aws.amazon.com/chime/latest/dg/proxy-phone-sessions.html>`__ in the *Amazon Chime Developer Guide*.
