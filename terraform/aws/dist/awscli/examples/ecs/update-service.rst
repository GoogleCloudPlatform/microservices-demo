**Example 1: To change the task definition used in a service**

The following ``update-service`` example updates the ``my-http-service`` service to use the ``amazon-ecs-sample`` task definition. ::

    aws ecs update-service --service my-http-service --task-definition amazon-ecs-sample

**Example 2: To change the number of tasks in a service**

The following ``update-service`` example updates the desired task count of the service ``my-http-service`` to 3. ::

    aws ecs update-service --service my-http-service --desired-count 3

For more information, see `Updating a Service <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/update-service.html>`_ in the *Amazon ECS Developer Guide*.