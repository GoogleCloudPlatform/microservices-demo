**To describe Elastic IP instances**

The following ``describe-elastic-ips`` commmand describes the Elastic IP addresses in a specified instance. ::

  aws opsworks --region us-east-1 describe-elastic-ips --instance-id b62f3e04-e9eb-436c-a91f-d9e9a396b7b0

*Output*::

  {
    "ElasticIps": [
        {
            "Ip": "192.0.2.0",
            "Domain": "standard",
            "Region": "us-west-2"
        }
    ]
  }

**More Information**

For more information, see Instances_ in the *AWS OpsWorks User Guide*.

.. _Instances: http://docs.aws.amazon.com/opsworks/latest/userguide/workinginstances.html

