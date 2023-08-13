**To unassign a volume from its instance**

The following example unassigns a registered Amazon Elastic Block Store (Amazon EBS) volume from its instance.
The volume is identified by its volume ID, which is the GUID that AWS OpsWorks assigns when
you register the volume with a stack, not the Amazon Elastic Compute Cloud (Amazon EC2) volume ID. ::

  aws opsworks --region us-east-1 unassign-volume --volume-id 8430177d-52b7-4948-9c62-e195af4703df

*Output*: None.

**More Information**

For more information, see `Unassigning Amazon EBS Volumes`_ in the *AWS OpsWorks User Guide*.

.. _`Unassigning Amazon EBS Volumes`: http://docs.aws.amazon.com/opsworks/latest/userguide/resources-detach.html#resources-detach-ebs

