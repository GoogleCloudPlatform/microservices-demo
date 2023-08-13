**To describe commands**

The following ``describe-commands`` commmand describes the commands in a specified instance. ::

  aws opsworks --region us-east-1 describe-commands --instance-id 8c2673b9-3fe5-420d-9cfa-78d875ee7687

*Output*::

  {
    "Commands": [
      {
        "Status": "successful",
        "CompletedAt": "2013-07-25T18:57:47+00:00",
        "InstanceId": "8c2673b9-3fe5-420d-9cfa-78d875ee7687",
        "DeploymentId": "6ed0df4c-9ef7-4812-8dac-d54a05be1029",
        "AcknowledgedAt": "2013-07-25T18:57:41+00:00",
        "LogUrl": "https://s3.amazonaws.com/prod_stage-log/logs/008c1a91-ec59-4d51-971d-3adff54b00cc?AWSAccessKeyId=AKIAIOSFODNN7EXAMPLE &Expires=1375394373&Signature=HkXil6UuNfxTCC37EPQAa462E1E%3D&response-cache-control=private&response-content-encoding=gzip&response-content- type=text%2Fplain",
        "Type": "undeploy",
        "CommandId": "008c1a91-ec59-4d51-971d-3adff54b00cc",
        "CreatedAt": "2013-07-25T18:57:34+00:00",
        "ExitCode": 0
      },
      {
        "Status": "successful",
        "CompletedAt": "2013-07-25T18:55:40+00:00",
        "InstanceId": "8c2673b9-3fe5-420d-9cfa-78d875ee7687",
        "DeploymentId": "19d3121e-d949-4ff2-9f9d-94eac087862a",
        "AcknowledgedAt": "2013-07-25T18:55:32+00:00",
        "LogUrl": "https://s3.amazonaws.com/prod_stage-log/logs/899d3d64-0384-47b6-a586-33433aad117c?AWSAccessKeyId=AKIAIOSFODNN7EXAMPLE &Expires=1375394373&Signature=xMsJvtLuUqWmsr8s%2FAjVru0BtRs%3D&response-cache-control=private&response-content-encoding=gzip&response-conten t-type=text%2Fplain",
        "Type": "deploy",
        "CommandId": "899d3d64-0384-47b6-a586-33433aad117c",
        "CreatedAt": "2013-07-25T18:55:29+00:00",
        "ExitCode": 0
      }
    ]
  }

**More Information**

For more information, see `AWS OpsWorks Lifecycle Events`_ in the *AWS OpsWorks User Guide*.

.. _`AWS OpsWorks Lifecycle Events`: http://docs.aws.amazon.com/opsworks/latest/userguide/workingcookbook-events.html

