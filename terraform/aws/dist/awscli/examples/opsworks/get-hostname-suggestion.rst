**To get the next hostname for a layer**

The following example gets the next generated hostname for a specified layer. The layer used for
this example is a Java Application Server layer with one instance. The stack's hostname theme is
the default, Layer_Dependent. ::

  aws opsworks --region us-east-1 get-hostname-suggestion --layer-id 888c5645-09a5-4d0e-95a8-812ef1db76a4

*Output*::

  {
    "Hostname": "java-app2", 
    "LayerId": "888c5645-09a5-4d0e-95a8-812ef1db76a4"
  }

**More Information**

For more information, see `Create a New Stack`_ in the *AWS OpsWorks User Guide*.

.. _`Create a New Stack`: http://docs.aws.amazon.com/opsworks/latest/userguide/workingstacks-creating.html

