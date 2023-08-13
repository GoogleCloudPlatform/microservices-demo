**Example 1: To describe a target group**

The following ``describe-target-groups`` example displays details for the specified target group. ::

    aws elbv2 describe-target-groups \
        --target-group-arns arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067

Output::

    {
        "TargetGroups": [
            {
                "TargetGroupName": "my-targets",
                "Protocol": "HTTP",
                "Port": 80,
                "VpcId": "vpc-3ac0fb5f",
                "TargetType": "instance",
                "HealthCheckEnabled": true,
                "UnhealthyThresholdCount": 2,
                "HealthyThresholdCount": 5,
                "HealthCheckPath": "/",
                "Matcher": {
                    "HttpCode": "200"
                },
                "HealthCheckProtocol": "HTTP",
                "HealthCheckPort": "traffic-port",
                "HealthCheckIntervalSeconds": 30,
                "HealthCheckTimeoutSeconds": 5,
                "TargetGroupArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067",
                "LoadBalancerArns": [
                    "arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188"
                ]
            }
        ]
    }

**Example 2: To describe all target groups for a load balancer**

The following ``describe-target-groups`` example displays details for all target groups for the specified load balancer. ::

    aws elbv2 describe-target-groups \
        --load-balancer-arn arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188

**Example 3: To describe all target groups**

The following ``describe-target-groups`` example dislplays details for all of your target groups. ::

    aws elbv2 describe-target-groups 
