**To create a layer**

The following ``create-layer`` command creates a PHP App Server layer named MyPHPLayer in a specified stack. ::

  aws opsworks create-layer --region us-east-1 --stack-id f6673d70-32e6-4425-8999-265dd002fec7 --type php-app --name MyPHPLayer --shortname myphplayer

*Output*::

  {
    "LayerId": "0b212672-6b4b-40e4-8a34-5a943cf2e07a"
  }

**More Information**

For more information, see `How to Create a Layer`_ in the *AWS OpsWorks User Guide*.

.. _`How to Create a Layer`: http://docs.aws.amazon.com/opsworks/latest/userguide/workinglayers-basics-create.html
