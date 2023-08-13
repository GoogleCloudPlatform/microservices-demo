**Example 1: To create an AMI from an Amazon EBS-backed instance**

The following ``create-image`` example creates an AMI from the specified instance. ::

    aws ec2 create-image \
        --instance-id i-1234567890abcdef0 \
        --name "My server" \
        --description "An AMI for my server"

Output::

    {
        "ImageId": "ami-0eab20fe36f83e1a8"
    }

For more information about specifying a block device mapping for your AMI, see `Specifying a block device mapping for an AMI <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html#create-ami-bdm>`__ in the *Amazon EC2 User Guide*.

**Example 2: To create an AMI from an Amazon EBS-backed instance without reboot**

The following ``create-image`` example creates an AMI and sets the --no-reboot parameter, so that the instance is not rebooted before the image is created. ::

    aws ec2 create-image \
        --instance-id i-0b09a25c58929de26 \
        --name "My server" \
        --no-reboot

Output::

    {
        "ImageId": "ami-01d7dcccb80665a0f"
    }

For more information about specifying a block device mapping for your AMI, see `Specifying a block device mapping for an AMI <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html#create-ami-bdm>`__ in the *Amazon EC2 User Guide*.
