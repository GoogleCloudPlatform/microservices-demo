**To describe a stack's registered Amazon RDS instances**

The following example describes the Amazon RDS instances registered with a specified stack. ::

  aws opsworks --region us-east-1 describe-rds-db-instances --stack-id d72553d4-8727-448c-9b00-f024f0ba1b06

*Output*: The following is the output for a stack with one registered RDS instance. ::

  {
    "RdsDbInstances": [
      {
        "Engine": "mysql", 
        "StackId": "d72553d4-8727-448c-9b00-f024f0ba1b06", 
        "MissingOnRds": false, 
        "Region": "us-west-2", 
        "RdsDbInstanceArn": "arn:aws:rds:us-west-2:123456789012:db:clitestdb", 
        "DbPassword": "*****FILTERED*****", 
        "Address": "clitestdb.cdlqlk5uwd0k.us-west-2.rds.amazonaws.com", 
        "DbUser": "cliuser", 
        "DbInstanceIdentifier": "clitestdb"
      }
    ]
  }


For more information, see `Resource Management`_ in the *AWS OpsWorks User Guide*.

.. _`Resource Management`: http://docs.aws.amazon.com/opsworks/latest/userguide/resources.html

