**To describe a stack's elastic load balancers**

The following ``describe-elastic-load-balancers`` command describes a specified stack's load balancers.  ::

  aws opsworks --region us-west-2 describe-elastic-load-balancers --stack-id 6f4660e5-37a6-4e42-bfa0-1358ebd9c182

*Output*: This particular stack has one load balancer.

::

  {
    "ElasticLoadBalancers": [
        {
            "SubnetIds": [
                "subnet-60e4ea04",
                "subnet-66e1c110"
            ],
            "Ec2InstanceIds": [],
            "ElasticLoadBalancerName": "my-balancer",
            "Region": "us-west-2",
            "LayerId": "344973cb-bf2b-4cd0-8d93-51cd819bab04",
            "AvailabilityZones": [
                "us-west-2a",
                "us-west-2b"
            ],
            "VpcId": "vpc-b319f9d4",
            "StackId": "6f4660e5-37a6-4e42-bfa0-1358ebd9c182",
            "DnsName": "my-balancer-2094040179.us-west-2.elb.amazonaws.com"
        }
    ]
  }

**More Information**

For more information, see Apps_ in the *AWS OpsWorks User Guide*.

.. _Apps: http://docs.aws.amazon.com/opsworks/latest/userguide/workingapps.html
