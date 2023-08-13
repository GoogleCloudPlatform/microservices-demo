**To delete an instance**

The following ``delete-instance`` example deletes a specified instance, which is identified by its instance ID. You can find an instance ID by opening the instance's details page in the AWS OpsWorks console, or by running the ``describe-instances`` command.

If the instance is online, you must first stop the instance by calling ``stop-instance``, and then you must wait until the instance has stopped. Run ``describe-instances`` to check the instance status.

To remove the instance's Amazon EBS volumes or Elastic IP addresses, add the ``--delete-volumes`` or ``--delete-elastic-ip`` arguments, respectively. ::

    aws opsworks delete-instance \
        --region us-east-1 \
        --instance-id 3a21cfac-4a1f-4ce2-a921-b2cfba6f7771

This command produces no output.

For more information, see `Deleting AWS OpsWorks Instances <https://docs.aws.amazon.com/opsworks/latest/userguide/workinginstances-delete.html>`__ in the *AWS OpsWorks User Guide*.