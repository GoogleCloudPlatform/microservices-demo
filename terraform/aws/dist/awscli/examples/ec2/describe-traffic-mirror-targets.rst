**To describe a Traffic Mirror Target**

The following ``describe-traffic-mirror-targets`` example displays details of the specified Traffic Mirror target. ::

    aws ec2 describe-traffic-mirror-targets \
        --traffic-mirror-target-id tmt-0dabe9b0a6EXAMPLE

Output::

    {
        "TrafficMirrorTargets": [
            {
                "TrafficMirrorTargetId": "tmt-0dabe9b0a6EXAMPLE",
                "NetworkLoadBalancerArn": "arn:aws:elasticloadbalancing:us-east-1:111122223333:loadbalancer/net/NLB/7cdec873fEXAMPLE",
                "Type": "network-load-balancer",
                "Description": "Example Network Load Balancer Target",
                "OwnerId": "111122223333",
                "Tags": []
            }
        ]
    }

For more information, see `View Traffic Mirror Target Details <https://docs.aws.amazon.com/vpc/latest/mirroring/traffic-mirroring-target.html#view-traffic-mirroring-targets>`__ in the *AWS Traffic Mirroring Guide*.
