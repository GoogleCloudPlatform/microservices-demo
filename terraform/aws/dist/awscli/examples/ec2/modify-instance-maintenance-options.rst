**Example 1: To disable the recovery behavior of an instance**

The following ``modify-instance-maintenance-options`` example disables simplified automatic recovery for a running or stopped instance. ::

    aws ec2 modify-instance-maintenance-options \
        --instance-id i-0abcdef1234567890 \
        --auto-recovery disabled 

Output::

    {
        "InstanceId": "i-0abcdef1234567890",
        "AutoRecovery": "disabled"
    }

For more information, see `Recover your instance <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-recover.html#instance-configuration-recovery>`__ in the *Amazon EC2 User Guide for Linux Instances*.

**Example 2: To set the recovery behavior of an instance to default**

The following ``modify-instance-maintenance-options`` example sets the automatic recovery behavior to default which enables simplified automatic recovery for supported instance types. ::

    aws ec2 modify-instance-maintenance-options \
        --instance-id i-0abcdef1234567890 \
        --auto-recovery default 

Output::

    {
        "InstanceId": "i-0abcdef1234567890",
        "AutoRecovery": "default"
    }

For more information, see `Recover your instance <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-recover.html#instance-configuration-recovery>`__ in the *Amazon EC2 User Guide for Linux Instances*.
