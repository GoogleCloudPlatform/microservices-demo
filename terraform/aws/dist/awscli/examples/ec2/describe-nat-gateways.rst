**To describe your NAT gateways**

This example describes all of your NAT gateways.

Command::

  aws ec2 describe-nat-gateways

Output::

  {
    "NatGateways": [
      {
        "NatGatewayAddresses": [
          {
            "PublicIp": "198.11.222.333", 
            "NetworkInterfaceId": "eni-9dec76cd", 
            "AllocationId": "eipalloc-89c620ec", 
            "PrivateIp": "10.0.0.149"
          }
        ], 
        "VpcId": "vpc-1a2b3c4d", 
        "Tags": [
                {
                    "Value": "IT", 
                    "Key": "Department"
                }
        ],
        "State": "available", 
        "NatGatewayId": "nat-05dba92075d71c408", 
        "SubnetId": "subnet-847e4dc2", 
        "CreateTime": "2015-12-01T12:26:55.983Z"
      }, 
      {
        "NatGatewayAddresses": [
          {
            "PublicIp": "1.2.3.12", 
            "NetworkInterfaceId": "eni-71ec7621", 
            "AllocationId": "eipalloc-5d42583f", 
            "PrivateIp": "10.0.0.77"
          }
        ], 
        "VpcId": "vpc-11aa22bb",
        "Tags": [
                {
                    "Value": "Finance", 
                    "Key": "Department"
                }
        ], 
        "State": "available", 
        "NatGatewayId": "nat-0a93acc57881d4199", 
        "SubnetId": "subnet-7f7e4d39",  
        "CreateTime": "2015-12-01T12:09:22.040Z"
      }
    ]
  }