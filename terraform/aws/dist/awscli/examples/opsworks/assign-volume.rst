**To assign a registered volume to an instance**

The following example assigns a registered Amazon Elastic Block Store (Amazon EBS) volume to an instance.
The volume is identified by its volume ID, which is the GUID that AWS OpsWorks assigns when
you register the volume with a stack, not the Amazon Elastic Compute Cloud (Amazon EC2) volume ID.
Before you run ``assign-volume``, you must first run ``update-volume`` to assign a mount point to the volume. ::

  aws opsworks --region us-east-1 assign-volume --instance-id 4d6d1710-ded9-42a1-b08e-b043ad7af1e2 --volume-id 26cf1d32-6876-42fa-bbf1-9cadc0bff938

*Output*: None.

**More Information**

For more information, see `Assigning Amazon EBS Volumes to an Instance`_ in the *AWS OpsWorks User Guide*.

.. _`Assigning Amazon EBS Volumes to an Instance`: http://docs.aws.amazon.com/opsworks/latest/userguide/resources-attach.html#resources-attach-ebs

