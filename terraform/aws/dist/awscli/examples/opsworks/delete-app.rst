**To delete an app**

The following example deletes a specified app, which is identified by its app ID.
You can obtain an app ID by going to the app's details page on the AWS OpsWorks console or by
running the ``describe-apps`` command. ::

  aws opsworks delete-app --region us-east-1 --app-id 577943b9-2ec1-4baf-a7bf-1d347601edc5

*Output*: None.

**More Information**

For more information, see `Apps`_ in the *AWS OpsWorks User Guide*.

.. _`Apps`: http://docs.aws.amazon.com/opsworks/latest/userguide/workingapps.html


