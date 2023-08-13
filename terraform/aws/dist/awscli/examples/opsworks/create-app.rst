**To create an app**

The following example creates a PHP app named SimplePHPApp from code stored in a GitHub repository.
The command uses the shorthand form of the application source definition. ::

  aws opsworks --region us-east-1 create-app --stack-id f6673d70-32e6-4425-8999-265dd002fec7 --name SimplePHPApp --type php --app-source Type=git,Url=git://github.com/amazonwebservices/opsworks-demo-php-simple-app.git,Revision=version1

*Output*::

  {
    "AppId": "6cf5163c-a951-444f-a8f7-3716be75f2a2"
  }

**To create an app with an attached database**

The following example creates a JSP app from code stored in .zip archive in a public S3 bucket.
It attaches an RDS DB instance to serve as the app's data store. The application and database sources are defined in separate
JSON files that are in the directory from which you run the command. ::

  aws opsworks --region us-east-1 create-app --stack-id 8c428b08-a1a1-46ce-a5f8-feddc43771b8 --name SimpleJSP --type java --app-source file://appsource.json --data-sources file://datasource.json 

The application source information is in ``appsource.json`` and contains the following. ::

  {
    "Type": "archive",
    "Url": "https://s3.amazonaws.com/jsp_example/simplejsp.zip"
  }

The database source information is in ``datasource.json`` and contains the following. ::

  [
    {
      "Type": "RdsDbInstance",
      "Arn": "arn:aws:rds:us-west-2:123456789012:db:clitestdb",
      "DatabaseName": "mydb"
    }
  ]
  
**Note**: For an RDS DB instance, you must first use ``register-rds-db-instance`` to register the instance with the stack.
For MySQL App Server instances, set ``Type`` to ``OpsworksMysqlInstance``. These instances are
created by AWS OpsWorks,
so they do not have to be registered.

*Output*::

  {
    "AppId": "26a61ead-d201-47e3-b55c-2a7c666942f8"
  }

For more information, see `Adding Apps`_ in the *AWS OpsWorks User Guide*.

.. _`Adding Apps`: http://docs.aws.amazon.com/opsworks/latest/userguide/workingapps-creating.html

