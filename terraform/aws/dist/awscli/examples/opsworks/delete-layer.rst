**To delete a layer**

The following example deletes a specified layer, which is identified by its layer ID.
You can obtain a layer ID by going to the layer's details page on the AWS OpsWorks console or by
running the ``describe-layers`` command.

**Note:** Before deleting a layer, you must use ``delete-instance`` to delete all of the layer's instances. ::

  aws opsworks delete-layer --region us-east-1 --layer-id a919454e-b816-4598-b29a-5796afb498ed

*Output*: None.

**More Information**

For more information, see `Deleting AWS OpsWorks Instances`_ in the *AWS OpsWorks User Guide*.

.. _`Deleting AWS OpsWorks Instances`: http://docs.aws.amazon.com/opsworks/latest/userguide/workinginstances-delete.html
