**To describe a task definition**

The following ``describe-task-definition`` example retrieves the details of a task definition. ::

    aws ecs describe-task-definition --task-definition hello_world:8

Output::

    {
        "taskDefinition": {
            "volumes": [],
            "taskDefinitionArn": "arn:aws:ecs:us-west-2:123456789012:task-definition/hello_world:8",
            "containerDefinitions": [
                {
                    "environment": [],
                    "name": "wordpress",
                    "links": [
                        "mysql"
                    ],
                    "mountPoints": [],
                    "image": "wordpress",
                    "essential": true,
                    "portMappings": [
                        {
                            "containerPort": 80,
                            "hostPort": 80
                        }
                    ],
                    "memory": 500,
                    "cpu": 10,
                    "volumesFrom": []
                },
                {
                    "environment": [
                        {
                            "name": "MYSQL_ROOT_PASSWORD",
                            "value": "password"
                        }
                    ],
                    "name": "mysql",
                    "mountPoints": [],
                    "image": "mysql",
                    "cpu": 10,
                    "portMappings": [],
                    "memory": 500,
                    "essential": true,
                    "volumesFrom": []
                }
            ],
            "family": "hello_world",
            "revision": 8
        }
    }

For more information, see `Amazon ECS Task Definitions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html>`_ in the *Amazon ECS Developer Guide*.
