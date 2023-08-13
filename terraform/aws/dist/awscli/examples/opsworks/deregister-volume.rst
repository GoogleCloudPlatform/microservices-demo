**To deregister an Amazon EBS volume**

The following example deregisters an EBS volume from its stack.
The volume is identified by its volume ID, which is the GUID that AWS OpsWorks assigned when
you registered the volume with the stack, not the EC2 volume ID. ::

  aws opsworks deregister-volume --region us-east-1 --volume-id 5c48ef52-3144-4bf5-beaa-fda4deb23d4d

*Output*: None.

**More Information**

For more information, see `Deregistering Amazon EBS Volumes`_ in the *AWS OpsWorks User Guide*.

.. _`Deregistering Amazon EBS Volumes`: http://docs.aws.amazon.com/opsworks/latest/userguide/resources-dereg.html#resources-dereg-ebs
