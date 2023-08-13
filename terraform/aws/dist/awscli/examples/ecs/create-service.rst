**Example 1: To create a service with a Fargate task**

The following ``create-service`` example shows how to create a service using a Fargate task. ::

    aws ecs create-service \
        --cluster MyCluster \
        --service-name MyService \
        --task-definition sample-fargate:1 \
        --desired-count 2 \
        --launch-type FARGATE \
        --platform-version LATEST \
        --network-configuration "awsvpcConfiguration={subnets=[subnet-12344321],securityGroups=[sg-12344321],assignPublicIp=ENABLED}" \
        --tags key=key1,value=value1 key=key2,value=value2 key=key3,value=value3

Output::

    {
        "service": {
            "serviceArn": "arn:aws:ecs:us-west-2:123456789012:service/MyCluster/MyService",
            "serviceName": "MyService",
              "clusterArn": "arn:aws:ecs:us-west-2:123456789012:cluster/MyCluster",
            "loadBalancers": [],
            "serviceRegistries": [],
            "status": "ACTIVE",
            "desiredCount": 2,
            "runningCount": 0,
            "pendingCount": 0,
            "launchType": "FARGATE",
            "platformVersion": "LATEST",
            "taskDefinition": "arn:aws:ecs:us-west-2:123456789012:task-definition/sample-fargate:1",
            "deploymentConfiguration": {
                "maximumPercent": 200,
                "minimumHealthyPercent": 100
            },
            "deployments": [
                {
                    "id": "ecs-svc/1234567890123456789",
                    "status": "PRIMARY",
                    "taskDefinition": "arn:aws:ecs:us-west-2:123456789012:task-definition/sample-fargate:1",
                    "desiredCount": 2,
                    "pendingCount": 0,
                    "runningCount": 0,
                    "createdAt": 1557119253.821,
                    "updatedAt": 1557119253.821,
                    "launchType": "FARGATE",
                    "platformVersion": "1.3.0",
                    "networkConfiguration": {
                        "awsvpcConfiguration": {
                            "subnets": [
                                "subnet-12344321"
                            ],
                            "securityGroups": [
                                "sg-12344321"
                            ],
                            "assignPublicIp": "ENABLED"
                        }
                    }
                }
            ],
            "roleArn": "arn:aws:iam::123456789012:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS",
            "events": [],
            "createdAt": 1557119253.821,
            "placementConstraints": [],
            "placementStrategy": [],
            "networkConfiguration": {
                "awsvpcConfiguration": {
                    "subnets": [
                        "subnet-12344321"
                    ],
                    "securityGroups": [
                        "sg-12344321"
                    ],
                    "assignPublicIp": "ENABLED"
                }
            },
            "schedulingStrategy": "REPLICA",
            "tags": [
                {
                    "key": "key1",
                    "value": "value1"
                },
                {
                    "key": "key2",
                    "value": "value2"
                },
                {
                    "key": "key3",
                    "value": "value3"
                }
            ],
            "enableECSManagedTags": false,
            "propagateTags": "NONE"
        }
    }

**Example 2: To create a service using the EC2 launch type**

The following ``create-service`` example shows how to create a service called ``ecs-simple-service`` with a task that uses the EC2 launch type. The service uses the ``sleep360`` task definition and it maintains 1 instantiation of the task. ::

    aws ecs create-service \
        --cluster MyCluster \
        --service-name ecs-simple-service \
        --task-definition sleep360:2 \
        --desired-count 1

Output::

    {
        "service": {
            "serviceArn": "arn:aws:ecs:us-west-2:123456789012:service/MyCluster/ecs-simple-service",
            "serviceName": "ecs-simple-service",
            "clusterArn": "arn:aws:ecs:us-west-2:123456789012:cluster/MyCluster",
            "loadBalancers": [],
            "serviceRegistries": [],
            "status": "ACTIVE",
            "desiredCount": 1,
            "runningCount": 0,
            "pendingCount": 0,
            "launchType": "EC2",
            "taskDefinition": "arn:aws:ecs:us-west-2:123456789012:task-definition/sleep360:2",
            "deploymentConfiguration": {
                "maximumPercent": 200,
                "minimumHealthyPercent": 100
            },
            "deployments": [
                {
                    "id": "ecs-svc/1234567890123456789",
                    "status": "PRIMARY",
                    "taskDefinition": "arn:aws:ecs:us-west-2:123456789012:task-definition/sleep360:2",
                    "desiredCount": 1,
                    "pendingCount": 0,
                    "runningCount": 0,
                    "createdAt": 1557206498.798,
                    "updatedAt": 1557206498.798,
                    "launchType": "EC2"
                }
            ],
            "events": [],
            "createdAt": 1557206498.798,
            "placementConstraints": [],
            "placementStrategy": [],
            "schedulingStrategy": "REPLICA",
            "enableECSManagedTags": false,
            "propagateTags": "NONE"
        }
    }

**Example 3: To create a service that uses an external deployment controller**

The following ``create-service`` example creates a service that uses an external deployment controller. ::

    aws ecs create-service \
        --cluster MyCluster \
        --service-name MyService \
        --deployment-controller type=EXTERNAL \
        --desired-count 1

Output::

    {
        "service": {
            "serviceArn": "arn:aws:ecs:us-west-2:123456789012:service/MyCluster/MyService",
            "serviceName": "MyService",
            "clusterArn": "arn:aws:ecs:us-west-2:123456789012:cluster/MyCluster",
            "loadBalancers": [],
            "serviceRegistries": [],
            "status": "ACTIVE",
            "desiredCount": 1,
            "runningCount": 0,
            "pendingCount": 0,
            "launchType": "EC2",
            "deploymentConfiguration": {
                "maximumPercent": 200,
                "minimumHealthyPercent": 100
            },
            "taskSets": [],
            "deployments": [],
            "roleArn": "arn:aws:iam::123456789012:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS",
            "events": [],
            "createdAt": 1557128207.101,
            "placementConstraints": [],
            "placementStrategy": [],
            "schedulingStrategy": "REPLICA",
            "deploymentController": {
                "type": "EXTERNAL"
            },
            "enableECSManagedTags": false,
            "propagateTags": "NONE"
        }
    }

**Example 4: To create a new service behind a load balancer**

The following ``create-service`` example shows how to create a service that is behind a load balancer. You must have a load balancer configured in the same Region as your container instance. This example uses the ``--cli-input-json`` option and a JSON input file called ``ecs-simple-service-elb.json`` with the following content::

    {
        "serviceName": "ecs-simple-service-elb",
        "taskDefinition": "ecs-demo",
        "loadBalancers": [
            {
                "loadBalancerName": "EC2Contai-EcsElast-123456789012",
                "containerName": "simple-demo",
                "containerPort": 80
            }
        ],
        "desiredCount": 10,
        "role": "ecsServiceRole"
    }

Command::

    aws ecs create-service \
        --cluster MyCluster \
        --service-name ecs-simple-service-elb \
        --cli-input-json file://ecs-simple-service-elb.json

Output::

    {
        "service": {
            "status": "ACTIVE",
            "taskDefinition": "arn:aws:ecs:us-west-2:123456789012:task-definition/ecs-demo:1",
            "pendingCount": 0,
            "loadBalancers": [
                {
                    "containerName": "ecs-demo",
                    "containerPort": 80,
                    "loadBalancerName": "EC2Contai-EcsElast-123456789012"
                }
            ],
            "roleArn": "arn:aws:iam::123456789012:role/ecsServiceRole",
            "desiredCount": 10,
            "serviceName": "ecs-simple-service-elb",
            "clusterArn": "arn:aws:ecs:<us-west-2:123456789012:cluster/MyCluster",
            "serviceArn": "arn:aws:ecs:us-west-2:123456789012:service/ecs-simple-service-elb",
            "deployments": [
                {
                    "status": "PRIMARY",
                    "pendingCount": 0,
                    "createdAt": 1428100239.123,
                    "desiredCount": 10,
                    "taskDefinition": "arn:aws:ecs:us-west-2:123456789012:task-definition/ecs-demo:1",
                    "updatedAt": 1428100239.123,
                    "id": "ecs-svc/1234567890123456789",
                    "runningCount": 0
                }
            ],
            "events": [],
            "runningCount": 0
        }
    }

For more information, see `Creating a Service <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-service.html>`_ in the *Amazon ECS Developer Guide*.