**Example 1: To allocate an Elastic IP address from Amazon's address pool**

The following ``allocate-address`` example allocates an Elastic IP address. Amazon EC2 selects the address from Amazon's address pool. ::

    aws ec2 allocate-address 

Output::

    {
        "PublicIp": "70.224.234.241",
        "AllocationId": "eipalloc-01435ba59eEXAMPLE",
        "PublicIpv4Pool": "amazon",
        "NetworkBorderGroup": "us-west-2",
        "Domain": "vpc"
    }

For more information, see `Elastic IP addresses <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html>`__ in the *Amazon EC2 User Guide*.

**Example 2: To allocate an Elastic IP address and associate it with a network border group**

The following ``allocate-address`` example allocates an Elastic IP address and associates it with the specified network border group. ::

    aws ec2 allocate-address \
        --network-border-group us-west-2-lax-1

Output::

    {
        "PublicIp": "70.224.234.241",
        "AllocationId": "eipalloc-e03dd489ceEXAMPLE",
        "PublicIpv4Pool": "amazon",
        "NetworkBorderGroup": "us-west-2-lax-1",
        "Domain": "vpc"
    }

For more information, see `Elastic IP addresses <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html>`__ in the *Amazon EC2 User Guide*.

**Example 3: To allocate an Elastic IP address from an address pool that you own**

The following ``allocate-address`` example allocates an Elastic IP address from an address pool that you have brought to your Amazon Web Services account. Amazon EC2 selects the address from the address pool. ::

    aws ec2 allocate-address \
        --public-ipv4-pool ipv4pool-ec2-1234567890abcdef0

Output::

    {
        "AllocationId": "eipalloc-02463d08ceEXAMPLE",
        "NetworkBorderGroup": "us-west-2",
        "CustomerOwnedIp": "18.218.95.81",
        "CustomerOwnedIpv4Pool": "ipv4pool-ec2-1234567890abcdef0",
        "Domain": "vpc"
        "NetworkBorderGroup": "us-west-2",
    }

For more information, see `Elastic IP addresses <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html>`__ in the *Amazon EC2 User Guide*.