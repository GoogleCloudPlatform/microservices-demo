**To run a task on your default cluster**

The following ``run-task`` example runs a task on the default cluster. ::

    aws ecs run-task --cluster default --task-definition sleep360:1

Output::

    {
        "tasks": [
            {
                "taskArn": "arn:aws:ecs:us-west-2:123456789012:task/a1b2c3d4-5678-90ab-ccdef-11111EXAMPLE",
                "overrides": {
                    "containerOverrides": [
                        {
                            "name": "sleep"
                        }
                    ]
                },
                "lastStatus": "PENDING",
                "containerInstanceArn": "arn:aws:ecs:us-west-2:123456789012:container-instance/a1b2c3d4-5678-90ab-ccdef-22222EXAMPLE",
                "desiredStatus": "RUNNING",
                "taskDefinitionArn": "arn:aws:ecs:us-west-2:123456789012:task-definition/sleep360:1",
                "containers": [
                    {
                        "containerArn": "arn:aws:ecs:us-west-2:123456789012:container/a1b2c3d4-5678-90ab-ccdef-33333EXAMPLE",
                        "taskArn": "arn:aws:ecs:us-west-2:123456789012:task/a1b2c3d4-5678-90ab-ccdef-11111EXAMPLE",
                        "lastStatus": "PENDING",
                        "name": "sleep"
                    }
                ]
            }
        ]
    }


For more information, see `Running Tasks <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_run_task.html>`_ in the *Amazon ECS Developer Guide*.