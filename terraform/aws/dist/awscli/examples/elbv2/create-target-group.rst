**Example 1: To create a target group to route traffic to instances registered by instance ID**

The following ``create-target-group`` example creates a target group for an Application Load Balancer where you register targets by instance ID (the target type is ``instance``). This target group uses the HTTP protocol, port 80, and the default health check settings for an HTTP target group. ::

    aws elbv2 create-target-group \
        --name my-targets \
        --protocol HTTP \
        --port 80 \
        --target-type instance \
        --vpc-id vpc-3ac0fb5f

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
                "TargetGroupArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067"
            }
        ]
    }

For more information, see `Create a target group <https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-target-group.html>`__ in the *User Guide for Application Load Balancers*.

**Example 2: To create a target group to route traffic to an IP addresses**

The following ``create-target-group`` example creates a target group for a Network Load Balancer where you register targets by IP address (the target type is ``ip``). This target group uses the TCP protocol, port 80, and the default health check settings for a TCP target group. ::

    aws elbv2 create-target-group \
        --name my-ip-targets \
        --protocol TCP \
        --port 80 \
        --target-type ip \
        --vpc-id vpc-3ac0fb5f

Output::

    {
        "TargetGroups": [
            {
                "TargetGroupName": "my-ip-targets",
                "Protocol": "TCP",
                "Port": 80,
                "VpcId": "vpc-3ac0fb5f",
                "TargetType": "ip",
                "HealthCheckEnabled": true,
                "UnhealthyThresholdCount": 3,
                "HealthyThresholdCount": 3,
                "HealthCheckProtocol": "TCP",
                "HealthCheckPort": "traffic-port",
                "HealthCheckIntervalSeconds": 30,
                "HealthCheckTimeoutSeconds": 10,
                "TargetGroupArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-ip-targets/b6bba954d1361c78"
            }
        ]
    }

For more information, see `Create a target group for your Network Load Balancer <https://docs.aws.amazon.com/elasticloadbalancing/latest/network/create-target-group.html>`__ in the *User Guide for Network Load Balancers*.

**Example 3: To create a target group to route traffic to a Lambda function**

The following ``create-target-group`` example creates a target group for an Application Load Balancer where the target is a Lambda function (the target type is ``lambda``). Health checks are disabled for this target group by default. ::

    aws elbv2 create-target-group \
        --name my-lambda-target \
        --target-type lambda

Output::

    {
        "TargetGroups": [
            {
                "TargetGroupName": "my-lambda-target",
                "TargetType": "lambda",
                "HealthCheckEnabled": false,
                "UnhealthyThresholdCount": 2,
                "HealthyThresholdCount": 5,
                "HealthCheckPath": "/",
                "Matcher": {
                    "HttpCode": "200"
                },
                "HealthCheckIntervalSeconds": 35,
                "HealthCheckTimeoutSeconds": 30,
                "TargetGroupArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-lambda-target/a3003e085dbb8ddc"
            }
        ]
    }

For more information, see `Lambda functions as targets <https://docs.aws.amazon.com/elasticloadbalancing/latest/application/lambda-functions.html>`__ in the *User Guide for Application Load Balancers*.

**Example 4: To create a target group to route traffic to a Gateway Load Balancer**

The following ``create-target-group`` example creates a target group for a Gateway Load Balancer where the target is an instance, and the target group protocol is GENEVE. ::

    aws elbv2 create-target-group \
        --name my-glb-targetgroup \
        --protocol GENEVE \
        --port 6081 \
        --target-type instance \
        --vpc-id vpc-838475fe

Output::

    {
        "TargetGroups": [
            {
                "TargetGroupArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-glb-targetgroup/00c3d57eacd6f40b6f",
                "TargetGroupName": "my-glb-targetgroup",
                "Protocol": "GENEVE",
                "Port": 6081,
                "VpcId": "vpc-838475fe",
                "HealthCheckProtocol": "TCP",
                "HealthCheckPort": "80",
                "HealthCheckEnabled": true,
                "HealthCheckIntervalSeconds": 10,
                "HealthCheckTimeoutSeconds": 5,
                "HealthyThresholdCount": 5,
                "UnhealthyThresholdCount": 2,
                "TargetType": "instance"
            }
        ]
    }

For more information, see `Create a target group for your Gateway Load Balancer <https://docs.aws.amazon.com/elasticloadbalancing/latest/gateway/create-target-group.html>`__ in the *User Guide for Gateway Load Balancers*.