**To describe account attributes**

The following ``describe-account-attributes`` command returns information about your
account's usage of AWS OpsWorks for Chef Automate resources.::

  aws opsworks-cm describe-account-attributes

The output for each account attribute entry returned by the command resembles the following.
*Output*::

  {
   "Attributes": [ 
      { 
         "Maximum": 5,
         "Name": "ServerLimit",
         "Used": 2
      }
   ]
  }

**More Information**

For more information, see `DescribeAccountAttributes`_ in the *AWS OpsWorks for Chef Automate API Reference*.

.. _`DescribeAccountAttributes`: http://docs.aws.amazon.com/opsworks-cm/latest/APIReference/API_DescribeAccountAttributes.html

