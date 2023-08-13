**To create a proxy session**

The following ``create-proxy-session`` example creates a proxy session with voice and SMS capabilities. ::

    aws chime create-proxy-session \
        --voice-connector-id abcdef1ghij2klmno3pqr4 \
        --participant-phone-numbers "+14015550101" "+12065550100" \
        --capabilities "Voice" "SMS"

Output::

    {
        "ProxySession": {
            "VoiceConnectorId": "abcdef1ghij2klmno3pqr4",
            "ProxySessionId": "123a4bc5-67d8-901e-2f3g-h4ghjk56789l",
            "Status": "Open",
            "ExpiryMinutes": 60,
            "Capabilities": [
                "SMS",
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
