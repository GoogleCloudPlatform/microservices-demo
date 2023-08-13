**Example 1: To change the default action to a forward action**

The following ``modify-listener`` example changes the default action (to a **forward** action)for the specified listener. ::

    aws elbv2 modify-listener \
        --listener-arn arn:aws:elasticloadbalancing:us-west-2:123456789012:listener/app/my-load-balancer/50dc6c495c0c9188/f2f7dc8efc522ab2 \
        --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-new-targets/2453ed029918f21f

Output::

    {
        "Listeners": [
            {
                "Protocol": "HTTP",
                "DefaultActions": [
                    {
                        "TargetGroupArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-new-targets/2453ed029918f21f",
                        "Type": "forward"
                    }
                ],
                "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188",
                "Port": 80,
                "ListenerArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:listener/app/my-load-balancer/50dc6c495c0c9188/f2f7dc8efc522ab2"
            }
        ]
    }

**Example 2: To change the default action to a redirect action**

The following ``modify-listener`` example changes the default action to a **redirect** action for the specified listener. ::

    aws elbv2 modify-listener \
        --listener-arn arn:aws:elasticloadbalancing:us-west-2:123456789012:listener/app/my-load-balancer/50dc6c495c0c9188/f2f7dc8efc522ab2 \
        --default-actions Type=redirect,TargetGroupArn=arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-new-targets/2453ed029918f21f

Output::

    {
    "Listeners": [
        {
            "Protocol": "HTTP",
            "DefaultActions": [
                {
                    "TargetGroupArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-new-targets/2453ed029918f21f",
                    "Type": "redirect"
                }
            ],
            "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188",
            "Port": 80,
            "ListenerArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:listener/app/my-load-balancer/50dc6c495c0c9188/f2f7dc8efc522ab2"
        }
      ]
    }

**Example 3: To change the server certificate**

This example changes the server certificate for the specified HTTPS listener. ::

    aws elbv2 modify-listener \
        --listener-arn arn:aws:elasticloadbalancing:us-west-2:123456789012:listener/app/my-load-balancer/50dc6c495c0c9188/0467ef3c8400ae65 \
        --certificates CertificateArn=arn:aws:iam::123456789012:server-certificate/my-new-server-cert

Output::

    {
        "Listeners": [
            {
                "Protocol": "HTTPS",
                "DefaultActions": [
                    {
                        "TargetGroupArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067",
                        "Type": "forward"
                    }
                ],
                "SslPolicy": "ELBSecurityPolicy-2015-05",
                "Certificates": [
                    {
                        "CertificateArn": "arn:aws:iam::123456789012:server-certificate/my-new-server-cert"
                    }
                ],
                "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188",
                "Port": 443,
                "ListenerArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:listener/app/my-load-balancer/50dc6c495c0c9188/0467ef3c8400ae65"
            }
        ]
    }