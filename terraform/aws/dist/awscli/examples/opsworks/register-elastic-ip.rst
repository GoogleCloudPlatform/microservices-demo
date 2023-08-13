**To register an Elastic IP address with a stack**

The following example registers an Elastic IP address, identified by its IP address, with a specified stack.

**Note:** The Elastic IP address must be in the same region as the stack. ::

  aws opsworks register-elastic-ip --region us-east-1 --stack-id d72553d4-8727-448c-9b00-f024f0ba1b06 --elastic-ip 54.148.130.96 

*Output* ::

  {
    "ElasticIp": "54.148.130.96"
  }

**More Information**

For more information, see `Registering Elastic IP Addresses with a Stack`_ in the *OpsWorks User Guide*.

.. _`Registering Elastic IP Addresses with a Stack`: http://docs.aws.amazon.com/opsworks/latest/userguide/resources-reg.html#resources-reg-eip
