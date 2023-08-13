**To describe deployments**

The following ``describe-deployments`` commmand describes the deployments in a specified stack. ::

  aws opsworks --region us-east-1 describe-deployments --stack-id 38ee91e2-abdc-4208-a107-0b7168b3cc7a

*Output*::

  {
    "Deployments": [
        {
            "StackId": "38ee91e2-abdc-4208-a107-0b7168b3cc7a",
            "Status": "successful",
            "CompletedAt": "2013-07-25T18:57:49+00:00",
            "DeploymentId": "6ed0df4c-9ef7-4812-8dac-d54a05be1029",
            "Command": {
                "Args": {},
                "Name": "undeploy"
            },
            "CreatedAt": "2013-07-25T18:57:34+00:00",
            "Duration": 15,
            "InstanceIds": [
                "8c2673b9-3fe5-420d-9cfa-78d875ee7687",
                "9e588a25-35b2-4804-bd43-488f85ebe5b7"
            ]
        },
        {
            "StackId": "38ee91e2-abdc-4208-a107-0b7168b3cc7a",
            "Status": "successful",
            "CompletedAt": "2013-07-25T18:56:41+00:00",
            "IamUserArn": "arn:aws:iam::123456789012:user/someuser",
            "DeploymentId": "19d3121e-d949-4ff2-9f9d-94eac087862a",
            "Command": {
                "Args": {},
                "Name": "deploy"
            },
            "InstanceIds": [
                "8c2673b9-3fe5-420d-9cfa-78d875ee7687",
                "9e588a25-35b2-4804-bd43-488f85ebe5b7"
            ],
            "Duration": 72,
            "CreatedAt": "2013-07-25T18:55:29+00:00"
        }
    ]
  }

**More Information**

For more information, see `Deploying Apps`_ in the *AWS OpsWorks User Guide*.

.. _`Deploying Apps`: http://docs.aws.amazon.com/opsworks/latest/userguide/workingapps-deploying.html

