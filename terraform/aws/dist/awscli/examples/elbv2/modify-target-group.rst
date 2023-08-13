**To modify the health check configuration for a target group**

This example changes the configuration of the health checks used to evaluate the health of the targets for the specified target group.

Command::

  aws elbv2 modify-target-group --target-group-arn arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-https-targets/2453ed029918f21f --health-check-protocol HTTPS --health-check-port 443
  
Output::

  {
    "TargetGroups": [
        {
            "HealthCheckIntervalSeconds": 30,
            "VpcId": "vpc-3ac0fb5f",
            "Protocol": "HTTPS",
            "HealthCheckTimeoutSeconds": 5,
            "HealthCheckProtocol": "HTTPS",
            "LoadBalancerArns": [
                "arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188"
            ],
            "UnhealthyThresholdCount": 2,
            "HealthyThresholdCount": 5,
            "TargetGroupArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-https-targets/2453ed029918f21f",
            "Matcher": {
                "HttpCode": "200"
            },
            "HealthCheckPort": "443",
            "Port": 443,
            "TargetGroupName": "my-https-targets"
        }
    ]
  }
