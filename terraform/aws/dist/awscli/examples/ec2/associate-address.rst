**To associate an Elastic IP addresses in EC2-Classic**

This example associates an Elastic IP address with an instance in EC2-Classic. If the command succeeds, no output is returned.

Command::

  aws ec2 associate-address --instance-id i-07ffe74c7330ebf53 --public-ip 198.51.100.0

**To associate an Elastic IP address in EC2-VPC**

This example associates an Elastic IP address with an instance in a VPC.

Command::

  aws ec2 associate-address --instance-id i-0b263919b6498b123 --allocation-id eipalloc-64d5890a

Output::

  {
      "AssociationId": "eipassoc-2bebb745"
  }

This example associates an Elastic IP address with a network interface.

Command::

  aws ec2 associate-address --allocation-id eipalloc-64d5890a --network-interface-id eni-1a2b3c4d

This example associates an Elastic IP with a private IP address that's associated with a network interface.

Command::

  aws ec2 associate-address --allocation-id eipalloc-64d5890a --network-interface-id eni-1a2b3c4d --private-ip-address 10.0.0.85

 
