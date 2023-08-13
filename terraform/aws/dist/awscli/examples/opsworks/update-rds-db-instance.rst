**To update a registered Amazon RDS DB instance**

The following example updates an Amazon RDS instance's master password value.
Note that this command does not change the RDS instance's master password, just the password that
you provide to AWS OpsWorks.
If this password does not match the RDS instance's password,
your application will not be able to connect to the database. ::

  aws opsworks --region us-east-1 update-rds-db-instance --db-password 123456789

*Output*: None.

**More Information**

For more information, see `Registering Amazon RDS Instances with a Stack`_ in the *AWS OpsWorks User Guide*.

.. _`Registering Amazon RDS Instances with a Stack`: http://docs.aws.amazon.com/opsworks/latest/userguide/resources-reg.html#resources-reg-rds

