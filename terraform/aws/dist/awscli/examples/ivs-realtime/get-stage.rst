**To get a stage's configuration information**

The following ``get-stage`` example gets the stage configuration for a specified stage ARN (Amazon Resource Name). ::

    aws ivs-realtime get-stage \
        --arn arn:aws:ivs:us-west-2:123456789012:stage/abcdABCDefgh

Output::

    {
        "stage": {
            "activeSessionId": "st-a1b2c3d4e5f6g",
            "arn": "arn:aws:ivs:us-west-2:123456789012:stage/abcdABCDefgh",
            "name": "test",
            "tags": {}
        }
    }

For more information, see `Enabling Multiple Hosts on an Amazon IVS Stream <https://docs.aws.amazon.com/ivs/latest/userguide/multiple-hosts.html>`__ in the *Amazon Interactive Video Service User Guide*.