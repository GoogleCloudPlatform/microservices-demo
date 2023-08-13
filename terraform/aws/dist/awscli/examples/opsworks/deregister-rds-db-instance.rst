**To deregister an Amazon RDS DB instance from a stack**

The following example deregisters an RDS DB instance, identified by its ARN, from its stack. ::

  aws opsworks deregister-rds-db-instance --region us-east-1 --rds-db-instance-arn arn:aws:rds:us-west-2:123456789012:db:clitestdb

*Output*: None.

**More Information**

For more information, see `Deregistering Amazon RDS Instances`_ in the *ASW OpsWorks User Guide*.

.. _`Deregistering Amazon RDS Instances`: http://docs.aws.amazon.com/opsworks/latest/userguide/resources-dereg.html#resources-dereg-rds


.. instance ID: clitestdb
   Master usernams: cliuser
   Master PWD: some23!pwd
   DB Name: mydb
   aws opsworks deregister-rds-db-instance --region us-east-1 --rds-db-instance-arn arn:aws:rds:us-west-2:645732743964:db:clitestdb