**To describe instances**

The following ``describe-instances`` commmand describes the instances in a specified stack::

  aws opsworks --region us-east-1 describe-instances --stack-id 8c428b08-a1a1-46ce-a5f8-feddc43771b8

*Output*: The following output example is for a stack with two instances. The first is a registered
EC2 instance, and the second was created by AWS OpsWorks.

::

  {
    "Instances": [
      {
        "StackId": "71c7ca72-55ae-4b6a-8ee1-a8dcded3fa0f",
        "PrivateDns": "ip-10-31-39-66.us-west-2.compute.internal",
        "LayerIds": [
          "26cf1d32-6876-42fa-bbf1-9cadc0bff938"
        ],
        "EbsOptimized": false,
        "ReportedOs": {
          "Version": "14.04",
          "Name": "ubuntu",
          "Family": "debian"
        },
        "Status": "online",
        "InstanceId": "4d6d1710-ded9-42a1-b08e-b043ad7af1e2",
        "SshKeyName": "US-West-2",
        "InfrastructureClass": "ec2",
        "RootDeviceVolumeId": "vol-d08ec6c1",
        "SubnetId": "subnet-b8de0ddd",
        "InstanceType": "t1.micro",
        "CreatedAt": "2015-02-24T20:52:49+00:00",
        "AmiId": "ami-35501205",
        "Hostname": "ip-192-0-2-0",
        "Ec2InstanceId": "i-5cd23551",
        "PublicDns": "ec2-192-0-2-0.us-west-2.compute.amazonaws.com",
        "SecurityGroupIds": [
          "sg-c4d3f0a1"
        ],
        "Architecture": "x86_64",
        "RootDeviceType": "ebs",
        "InstallUpdatesOnBoot": true,
        "Os": "Custom",
        "VirtualizationType": "paravirtual",
        "AvailabilityZone": "us-west-2a",
        "PrivateIp": "10.31.39.66",
        "PublicIp": "192.0.2.06",
        "RegisteredBy": "arn:aws:iam::123456789102:user/AWS/OpsWorks/OpsWorks-EC2Register-i-5cd23551"
      },
      {
        "StackId": "71c7ca72-55ae-4b6a-8ee1-a8dcded3fa0f",
        "PrivateDns": "ip-10-31-39-158.us-west-2.compute.internal",
        "SshHostRsaKeyFingerprint": "69:6b:7b:8b:72:f3:ed:23:01:00:05:bc:9f:a4:60:c1",
        "LayerIds": [
          "26cf1d32-6876-42fa-bbf1-9cadc0bff938"
        ],
        "EbsOptimized": false,
        "ReportedOs": {},
        "Status": "booting",
        "InstanceId": "9b137a0d-2f5d-4cc0-9704-13da4b31fdcb",
        "SshKeyName": "US-West-2",
        "InfrastructureClass": "ec2",
        "RootDeviceVolumeId": "vol-e09dd5f1",
        "SubnetId": "subnet-b8de0ddd",
        "InstanceProfileArn": "arn:aws:iam::123456789102:instance-profile/aws-opsworks-ec2-role",
        "InstanceType": "c3.large",
        "CreatedAt": "2015-02-24T21:29:33+00:00",
        "AmiId": "ami-9fc29baf",
        "SshHostDsaKeyFingerprint": "fc:87:95:c3:f5:e1:3b:9f:d2:06:6e:62:9a:35:27:e8",
        "Ec2InstanceId": "i-8d2dca80",
        "PublicDns": "ec2-192-0-2-1.us-west-2.compute.amazonaws.com",
        "SecurityGroupIds": [
          "sg-b022add5",
          "sg-b122add4"
        ],
        "Architecture": "x86_64",
        "RootDeviceType": "ebs",
        "InstallUpdatesOnBoot": true,
        "Os": "Amazon Linux 2014.09",
        "VirtualizationType": "paravirtual",
        "AvailabilityZone": "us-west-2a",
        "Hostname": "custom11",
        "PrivateIp": "10.31.39.158",
        "PublicIp": "192.0.2.0"
      }
    ]
  }

**More Information**

For more information, see `Instances`_ in the *AWS OpsWorks User Guide*.

.. _`Instances`: http://docs.aws.amazon.com/opsworks/latest/userguide/workinginstances.html

