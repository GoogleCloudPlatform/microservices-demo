**To modify the settings for your cluster**

The following ``update-cluster-settings`` example enables CloudWatch Container Insights for the ``default`` cluster. ::

    aws ecs update-cluster-settings \
        --cluster default \
        --settings name=containerInsights,value=enabled

Output::

    {
        "cluster": {
            "clusterArn": "arn:aws:ecs:us-west-2:123456789012:cluster/MyCluster",
            "clusterName": "default",
            "status": "ACTIVE",
            "registeredContainerInstancesCount": 0,
            "runningTasksCount": 0,
            "pendingTasksCount": 0,
            "activeServicesCount": 0,
            "statistics": [],
            "tags": [],
            "settings": [
                {
                    "name": "containerInsights",
                    "value": "enabled"
                }
            ]
        }
    }

For more information, see `Modifying Account Settings <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-modifying-longer-id-settings.html>`__ in the *Amazon ECS Developer Guide*.