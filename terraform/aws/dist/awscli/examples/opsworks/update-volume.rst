**To update a registered volume**

The following example updates a registered Amazon Elastic Block Store (Amazon EBS) volume's mount point.
The volume is identified by its volume ID, which is the GUID that AWS OpsWorks assigns to the volume when
you register it with a stack, not the Amazon Elastic Compute Cloud (Amazon EC2) volume ID.::

  aws opsworks --region us-east-1 update-volume --volume-id 8430177d-52b7-4948-9c62-e195af4703df --mount-point /mnt/myvol

*Output*: None.

**More Information**

For more information, see `Assigning Amazon EBS Volumes to an Instance`_ in the *AWS OpsWorks User Guide*.

.. _`Assigning Amazon EBS Volumes to an Instance`: http://docs.aws.amazon.com/opsworks/latest/userguide/resources-attach.html#resources-attach-ebs

