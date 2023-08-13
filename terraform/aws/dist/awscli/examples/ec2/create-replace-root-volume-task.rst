**Example 1: To restore a root volume to its initial launch state**

The following ``create-replace-root-volume-task`` example restores the root volume of instance i-0123456789abcdefa to its initial launch state. ::

    aws ec2 create-replace-root-volume-task \
        --instance-id i-0123456789abcdefa

Output::

    {
        "ReplaceRootVolumeTask": 
        {
            "InstanceId": "i-0123456789abcdefa", 
                "ReplaceRootVolumeTaskId": "replacevol-0111122223333abcd", 
                "TaskState": "pending", 
                "StartTime": "2022-03-14T15:06:38Z", 
                "Tags": []
        }
    }

For more information, see `Replace a root volume <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-restoring-volume.html#replace-root>`__ in the *Amazon Elastic Compute Cloud User Guide*.

**Example 2: To restore a root volume to a specific snapshot**

The following ``create-replace-root-volume-task`` example restores the root volume of instance i-0123456789abcdefa to snapshot snap-0abcdef1234567890. ::

    aws ec2 create-replace-root-volume-task \
        --instance-id i-0123456789abcdefa \
        --snapshot-id  snap-0abcdef1234567890

Output::

    {
        "ReplaceRootVolumeTask": 
        {
            "InstanceId": "i-0123456789abcdefa", 
            "ReplaceRootVolumeTaskId": "replacevol-0555566667777abcd", 
            "TaskState": "pending", 
            "StartTime": "2022-03-14T15:16:28Z", 
            "Tags": []
        }
    }

For more information, see `Replace a root volume <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-restoring-volume.html#replace-root>`__ in the *Amazon Elastic Compute Cloud User Guide*.