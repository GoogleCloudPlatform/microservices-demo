**To get a list of stage participant events**

The following ``list-participant-events`` example lists all participant events for a specified participant ID and session ID of a specified stage ARN (Amazon Resource Name). ::

    aws ivs-realtime list-participant-events \
        --stage-arn arn:aws:ivs:us-west-2:123456789012:stage/abcdABCDefgh \
        --session-id st-a1b2c3d4e5f6g \
        --participant-id abCDEf12GHIj

Output::

    {
        "events": [
            {
                "eventTime": "2023-04-26T20:36:28+00:00",
                "name": "LEFT",
                "participantId": "abCDEf12GHIj"
            },
            {
                "eventTime": "2023-04-26T20:36:28+00:00",
                "name": "PUBLISH_STOPPED",
                "participantId": "abCDEf12GHIj"
            },
            {
                "eventTime": "2023-04-26T20:30:34+00:00",
                "name": "JOINED",
                "participantId": "abCDEf12GHIj"
            },
            {
                "eventTime": "2023-04-26T20:30:34+00:00",
                "name": "PUBLISH_STARTED",
                "participantId": "abCDEf12GHIj"
            }
        ]
    }

For more information, see `Enabling Multiple Hosts on an Amazon IVS Stream <https://docs.aws.amazon.com/ivs/latest/userguide/multiple-hosts.html>`__ in the *Amazon Interactive Video Service User Guide*.