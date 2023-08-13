**To create a stage**

The following ``create-stage`` example creates a stage and stage participant token for a specified user. ::

    aws ivs-realtime create-stage \
        --name stage1 \
        --participant-token-configurations userId=alice

Output::

    {
        "participantTokens": [
            {
                "participantId": "ABCDEfghij01234KLMN5678",
                "token": "a1b2c3d4567890ab",
                "userId": "alice"
            }
        ],
        "stage": {
            "activeSessionId": "st-a1b2c3d4e5f6g",
            "arn": "arn:aws:ivs:us-west-2:123456789012:stage/abcdABCDefgh",
            "name": "stage1",
            "tags": {}
        }
    }

For more information, see `Enabling Multiple Hosts on an Amazon IVS Stream <https://docs.aws.amazon.com/ivs/latest/userguide/multiple-hosts.html>`__ in the *Amazon Interactive Video Service User Guide*.