**Example 1: To describe the security group rules using the security group ID**

The following ``describe-security-group-rules`` example describes the security group rules of a specified security group. Use the ``filter`` parameter to enter the ``group-id`` of the security group. ::

    aws ec2 describe-security-group-rules \
        --filter Name="group-id",Values="sg-1234567890abcdef0"

Output::

    {
        "SecurityGroupRules": [
            {
                "SecurityGroupRuleId": "sgr-abcdef01234567890",
                "GroupId": "sg-1234567890abcdef0",
                "GroupOwnerId": "111122223333",
                "IsEgress": false,
                "IpProtocol": "-1",
                "FromPort": -1,
                "ToPort": -1,
                "ReferencedGroupInfo": {
                    "GroupId": "sg-1234567890abcdef0",
                    "UserId": "111122223333"
                },
                "Tags": []
            },
            {
                "SecurityGroupRuleId": "sgr-bcdef01234567890a",
                "GroupId": "sg-1234567890abcdef0",
                "GroupOwnerId": "111122223333",
                "IsEgress": true,
                "IpProtocol": "-1",
                "FromPort": -1,
                "ToPort": -1,
                "CidrIpv6": "::/0",
                "Tags": []
            },
            {
                "SecurityGroupRuleId": "sgr-cdef01234567890ab",
                "GroupId": "sg-1234567890abcdef0",
                "GroupOwnerId": "111122223333",
                "IsEgress": true,
                "IpProtocol": "-1",
                "FromPort": -1,
                "ToPort": -1,
                "CidrIpv4": "0.0.0.0/0",
                "Tags": []
            }
        ]
    }

For more information about security group rules, see `Security group rules <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules.html>` in the *Amazon EC2 User Guide*.

**Example 2: To describe a security group rule using the security group rule ID**

The following ``describe-security-group-rules`` example describes a specified security group rule. Use the ``security-group-rule-ids`` parameter to specify the security group rule ID. ::

    aws ec2 describe-security-group-rules \
        --security-group-rule-ids sgr-cdef01234567890ab

Output::

    {
        "SecurityGroupRules": [
            {
                "SecurityGroupRuleId": "sgr-cdef01234567890ab",
                "GroupId": "sg-1234567890abcdef0",
                "GroupOwnerId": "111122223333",
                "IsEgress": true,
                "IpProtocol": "-1",
                "FromPort": -1,
                "ToPort": -1,
                "CidrIpv4": "0.0.0.0/0",
                "Tags": []
            }
        ]
    }

For more information about security group rules, see `Security group rules <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules.html>` in the *Amazon EC2 User Guide*.