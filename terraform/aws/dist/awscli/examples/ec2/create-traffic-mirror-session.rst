**To create a Traffic Mirror Session**

The following ``create-traffic-mirror-session`` command creates a traffic mirror sessions for the specified source and target for 25 bytes of the packet. ::

    aws ec2 create-traffic-mirror-session \
        --description "example session" \
        --traffic-mirror-target-id tmt-07f75d8feeEXAMPLE \
        --network-interface-id eni-070203f901EXAMPLE \
        --session-number 1  \
        --packet-length 25 \
        --traffic-mirror-filter-id tmf-04812ff784EXAMPLE

Output::

    {
        "TrafficMirrorSession": {
            "TrafficMirrorSessionId": "tms-08a33b1214EXAMPLE",
            "TrafficMirrorTargetId": "tmt-07f75d8feeEXAMPLE",
            "TrafficMirrorFilterId": "tmf-04812ff784EXAMPLE",
            "NetworkInterfaceId": "eni-070203f901EXAMPLE",
            "OwnerId": "111122223333",
            "PacketLength": 25,
            "SessionNumber": 1,
            "VirtualNetworkId": 7159709,
            "Description": "example session",
            "Tags": []
        },
        "ClientToken": "5236cffc-ee13-4a32-bb5b-388d9da09d96"
    }

For more information, see `Create a Traffic Mirror Session <https://docs.aws.amazon.com/vpc/latest/mirroring/traffic-mirroring-session.html#create-traffic-mirroring-session>`__ in the *AWS Traffic Mirroring Guide*.
