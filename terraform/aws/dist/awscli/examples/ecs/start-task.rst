**To start a new task**

The following ``start-task`` starts a task using the latest revision of the ``sleep360`` task definition on the specified container instance in the default cluster. ::

    aws ecs start-task \
        --task-definition sleep360 \
        --container-instances 765936fadbdd46b5991a4bd70c2a43d4

Output::

    {
        "tasks": [
            {
                "taskArn": "arn:aws:ecs:us-west-2:130757420319:task/default/666fdccc2e2d4b6894dd422f4eeee8f8",
                "clusterArn": "arn:aws:ecs:us-west-2:130757420319:cluster/default",
                "taskDefinitionArn": "arn:aws:ecs:us-west-2:130757420319:task-definition/sleep360:3",
                "containerInstanceArn": "arn:aws:ecs:us-west-2:130757420319:container-instance/default/765936fadbdd46b5991a4bd70c2a43d4",
                "overrides": {
                    "containerOverrides": [
                        {
                            "name": "sleep"
                        }
                    ]
                },
                "lastStatus": "PENDING",
                "desiredStatus": "RUNNING",
                "cpu": "128",
                "memory": "128",
                "containers": [
                    {
                        "containerArn": "arn:aws:ecs:us-west-2:130757420319:container/75f11ed4-8a3d-4f26-a33b-ad1db9e02d41",
                        "taskArn": "arn:aws:ecs:us-west-2:130757420319:task/default/666fdccc2e2d4b6894dd422f4eeee8f8",
                        "name": "sleep",
                        "lastStatus": "PENDING",
                        "networkInterfaces": [],
                        "cpu": "10",
                        "memory": "10"
                    }
                ],
                "version": 1,
                "createdAt": 1563421494.186,
                "group": "family:sleep360",
                "launchType": "EC2",
                "attachments": [],
                "tags": []
            }
        ],
        "failures": []
    }
