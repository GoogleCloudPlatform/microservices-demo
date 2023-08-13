**To create a network interface**

This example creates a network interface for the specified subnet.

Command::

  aws ec2 create-network-interface --subnet-id subnet-9d4a7b6c --description "my network interface" --groups sg-903004f8 --private-ip-address 10.0.2.17

Output::

  {
      "NetworkInterface": {
          "Status": "pending",
          "MacAddress": "02:1a:80:41:52:9c",
          "SourceDestCheck": true,
          "VpcId": "vpc-a01106c2",
          "Description": "my network interface",
          "NetworkInterfaceId": "eni-e5aa89a3",
          "PrivateIpAddresses": [
              {
                  "Primary": true,
                  "PrivateIpAddress": "10.0.2.17"
              }
          ],
          "RequesterManaged": false,
          "AvailabilityZone": "us-east-1d",
          "Ipv6Addresses": [], 
          "Groups": [
              {
                  "GroupName": "default",
                  "GroupId": "sg-903004f8"
              }
          ],
          "SubnetId": "subnet-9d4a7b6c",
          "OwnerId": "123456789012",
          "TagSet": [],
          "PrivateIpAddress": "10.0.2.17"
      }  
  }