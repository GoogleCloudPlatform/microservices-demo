**To modify the account setting for your IAM user account**

The following ``put-account-setting`` example enables the ``serviceLongArnFormat`` account setting for your IAM user account. ::

    aws ecs put-account-setting --name serviceLongArnFormat --value enabled

Output::

    {
        "setting": {
            "name": "serviceLongArnFormat",
            "value": "enabled",
            "principalArn": "arn:aws:iam::130757420319:user/your_username"
        }
    }

For more information, see `Modifying Account Settings <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-modifying-longer-id-settings.html>`__ in the *Amazon ECS Developer Guide*.
