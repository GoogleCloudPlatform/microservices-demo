**To describe RAID arrays**

The following example describes the RAID arrays attached to the instances in a specified stack. ::

  aws opsworks --region us-east-1 describe-raid-arrays --stack-id d72553d4-8727-448c-9b00-f024f0ba1b06

*Output*: The following is the output for a stack with one RAID array. ::

  {
    "RaidArrays": [
      {
        "StackId": "d72553d4-8727-448c-9b00-f024f0ba1b06", 
        "AvailabilityZone": "us-west-2a", 
        "Name": "Created for php-app1", 
        "NumberOfDisks": 2, 
        "InstanceId": "9f14adbc-ced5-43b6-bf01-e7d0db6cf2f7", 
        "RaidLevel": 0, 
        "VolumeType": "standard", 
        "RaidArrayId": "f2d4e470-5972-4676-b1b8-bae41ec3e51c", 
        "Device": "/dev/md0", 
        "MountPoint": "/mnt/workspace", 
        "CreatedAt": "2015-02-26T23:53:09+00:00", 
        "Size": 100
      } 
    ]
  }

For more information, see `EBS Volumes`_ in the *AWS OpsWorks User Guide*.

.. _`EBS Volumes`: http://docs.aws.amazon.com/opsworks/latest/userguide/workinglayers-basics-edit.html#workinglayers-basics-edit-ebs

