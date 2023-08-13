**Example 1: To describe the specified Auto Scaling group**

This example describes the specified Auto Scaling group. ::

    aws autoscaling describe-auto-scaling-groups \
        --auto-scaling-group-name my-asg

Output::

    {
        "AutoScalingGroups": [
            {
                "AutoScalingGroupName": "my-asg",
                "AutoScalingGroupARN": "arn:aws:autoscaling:us-west-2:123456789012:autoScalingGroup:930d940e-891e-4781-a11a-7b0acd480f03:autoScalingGroupName/my-asg",
                "LaunchTemplate": {
                    "LaunchTemplateName": "my-launch-template",
                    "Version": "1",
                    "LaunchTemplateId": "lt-1234567890abcde12"
                },
                "MinSize": 0,
                "MaxSize": 1,
                "DesiredCapacity": 1,
                "DefaultCooldown": 300,
                "AvailabilityZones": [
                    "us-west-2a",
                    "us-west-2b",
                    "us-west-2c"
                ],
                "LoadBalancerNames": [],
                "TargetGroupARNs": [],
                "HealthCheckType": "EC2",
                "HealthCheckGracePeriod": 0,
                "Instances": [
                    {
                        "InstanceId": "i-06905f55584de02da",
                        "InstanceType": "t2.micro",
                        "AvailabilityZone": "us-west-2a",
                        "HealthStatus": "Healthy",
                        "LifecycleState": "InService",
                        "ProtectedFromScaleIn": false,
                        "LaunchTemplate": {
                            "LaunchTemplateName": "my-launch-template",
                            "Version": "1",
                            "LaunchTemplateId": "lt-1234567890abcde12"
                        }
                    }
                ],
                "CreatedTime": "2020-10-28T02:39:22.152Z",
                "VPCZoneIdentifier": "subnet-5ea0c127,subnet-6194ea3b,subnet-c934b782",
                "SuspendedProcesses": [],
                "EnabledMetrics": [],
                "Tags": [],
                "TerminationPolicies": [
                    "Default"
                ],
                "NewInstancesProtectedFromScaleIn": false,
                "ServiceLinkedRoleARN":"arn"
            }
        ]
    }

**Example 2: To describe the first 100 specified Auto Scaling group**

This example describes the specified Auto Scaling groups. It allows you to specify up to 100 group names. ::

    aws autoscaling describe-auto-scaling-groups \
        --max-items 100 \
        --auto-scaling-group-name "group1" "group2" "group3" "group4"

See example 1 for sample output.

**Example 3: To describe an Auto Scaling group in the specified region**

This example describes the Auto Scaling groups in the specified region, up to a maximum of 75 groups. ::

    aws autoscaling describe-auto-scaling-groups \
        --max-items 75 \
        --region us-east-1

See example 1 for sample output.

**Example 4: To describe the specified number of Auto Scaling group**

To return a specific number of Auto Scaling groups, use the ``--max-items`` option. ::

    aws autoscaling describe-auto-scaling-groups \
        --max-items 1

See example 1 for sample output.

If the output includes a ``NextToken`` field, there are more groups. To get the additional groups, use the value of this field with the ``--starting-token`` option in a subsequent call as follows. ::

    aws autoscaling describe-auto-scaling-groups --starting-token Z3M3LMPEXAMPLE

See example 1 for sample output.
