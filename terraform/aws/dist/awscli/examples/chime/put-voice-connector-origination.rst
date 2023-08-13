**To set up origination settings**

The following ``put-voice-connector-origination`` example sets up the origination host, port, protocol, priority, and weight for the specified Amazon Chime Voice Connector. ::

    aws chime put-voice-connector-origination \
        --voice-connector-id abcdef1ghij2klmno3pqr4 \
        --origination Routes=[{Host="10.24.34.0",Port=1234,Protocol="TCP",Priority=1,Weight=5}],Disabled=false

Output::

    {
        "Origination": {
            "Routes": [
                {
                    "Host": "10.24.34.0",
                    "Port": 1234,
                    "Protocol": "TCP",
                    "Priority": 1,
                    "Weight": 5
                }
            ],
            "Disabled": false
        }
    }

For more information, see `Working with Amazon Chime Voice Connectors <https://docs.aws.amazon.com/chime/latest/ag/voice-connectors.html>`__ in the *Amazon Chime Administration Guide*.
