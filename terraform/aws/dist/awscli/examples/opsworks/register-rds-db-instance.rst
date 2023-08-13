**To register an Amazon RDS instance with a stack**

The following example registers an Amazon RDS DB instance, identified by its Amazon Resource Name (ARN), with a specified stack.
It also specifies the instance's master username and password. Note that AWS OpsWorks does not validate either of these
values. If either one is incorrect, your application will not be able to connect to the database. ::

  aws opsworks register-rds-db-instance --region us-east-1 --stack-id d72553d4-8727-448c-9b00-f024f0ba1b06 --rds-db-instance-arn arn:aws:rds:us-west-2:123456789012:db:clitestdb  --db-user cliuser --db-password some23!pwd

*Output*: None.

**More Information**

For more information, see `Registering Amazon RDS Instances with a Stack`_ in the *AWS OpsWorks User Guide*.

.. _`Registering Amazon RDS Instances with a Stack`: http://docs.aws.amazon.com/opsworks/latest/userguide/resources-reg.html#resources-reg-rds
