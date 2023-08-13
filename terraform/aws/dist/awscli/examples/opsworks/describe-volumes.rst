**To describe a stack's volumes**

The following example describes a stack's EBS volumes. ::

  aws opsworks --region us-east-1 describe-volumes --stack-id 8c428b08-a1a1-46ce-a5f8-feddc43771b8

*Output*::

  {
    "Volumes": [
      {
        "Status": "in-use",
        "AvailabilityZone": "us-west-2a",
        "Name": "CLITest",
        "InstanceId": "dfe18b02-5327-493d-91a4-c5c0c448927f",
        "VolumeType": "standard",
        "VolumeId": "56b66fbd-e1a1-4aff-9227-70f77118d4c5",
        "Device": "/dev/sdi",
        "Ec2VolumeId": "vol-295c1638",
        "MountPoint": "/mnt/myvolume",
        "Size": 1
      }
    ]
  }

**More Information**

For more information, see `Resource Management`_ in the *AWS OpsWorks User Guide*.

.. _`Resource Management`: http://docs.aws.amazon.com/opsworks/latest/userguide/resources.html

