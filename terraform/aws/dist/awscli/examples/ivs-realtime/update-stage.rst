**To update a stage's configuration**

The following ``update-stage`` example updates a stage for a specified stage ARN to update the stage name. ::

    aws ivs-realtime update-stage \
        --arn arn:aws:ivs:us-west-2:123456789012:stage/abcdABCDefgh \
        --name stage1a

Output::

    {
        "stage": {
            "arn": "arn:aws:ivs:us-west-2:123456789012:stage/abcdABCDefgh",
            "name": "stage1a"
        }
    }

For more information, see `Enabling Multiple Hosts on an Amazon IVS Stream <https://docs.aws.amazon.com/ivs/latest/userguide/multiple-hosts.html>`__ in the *Amazon Interactive Video Service User Guide*.