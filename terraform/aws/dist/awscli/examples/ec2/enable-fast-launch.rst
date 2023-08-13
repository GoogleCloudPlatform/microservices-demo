**To start fast launching for an image**

The following ``enable-fast-launch`` example starts fast launching on the specified AMI and sets the maximum number of parallel instances to launch to 6. The type of resource to use to pre-provision the AMI is set to ``snapshot``, which is also the default value. ::

    aws ec2 enable-fast-launch \
        --image-id ami-01234567890abcedf \
        --max-parallel-launches 6 \
        --resource-type snapshot

Output::

    {
        "ImageId": "ami-01234567890abcedf",
        "ResourceType": "snapshot",
        "SnapshotConfiguration": {
            "TargetResourceCount": 10
        },
        "LaunchTemplate": {},
        "MaxParallelLaunches": 6,
        "OwnerId": "0123456789123",
        "State": "enabling",
        "StateTransitionReason": "Client.UserInitiated",
        "StateTransitionTime": "2022-01-27T22:16:03.199000+00:00"
    }

For more information about configuring a Windows AMI for faster launching, see `Configure your AMI for faster launching <https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/windows-ami-version-history.html#win-ami-config-fast-launch>`__ in the *Amazon EC2 User Guide*.