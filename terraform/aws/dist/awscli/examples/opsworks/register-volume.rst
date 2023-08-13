**To register an Amazon EBS volume with a stack**

The following example registers an Amazon EBS volume, identified by its volume ID, with a specified stack. ::

  aws opsworks register-volume --region us-east-1 --stack-id d72553d4-8727-448c-9b00-f024f0ba1b06 --ec-2-volume-id vol-295c1638

*Output*::

  {
    "VolumeId": "ee08039c-7cb7-469f-be10-40fb7f0c05e8"
  }


**More Information**

For more information, see `Registering Amazon EBS Volumes with a Stack`_ in the *AWS OpsWorks User Guide*.

.. _`Registering Amazon EBS Volumes with a Stack`: http://docs.aws.amazon.com/opsworks/latest/userguide/resources-reg.html#resources-reg-ebs
