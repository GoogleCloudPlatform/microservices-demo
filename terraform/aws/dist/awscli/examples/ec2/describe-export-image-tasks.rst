**To monitor an export image task**

The following ``describe-export-image-tasks`` example checks the status of the specified export image task. ::

    aws ec2 describe-export-image-tasks \
        --export-image-task-id export-ami-1234567890abcdef0

Output for an export image task that is in progress::

    {
        "ExportImageTasks": [
            {
                "ExportImageTaskId": "export-ami-1234567890abcdef0"
                "Progress": "21",
                "S3ExportLocation": {
                    "S3Bucket": "my-export-bucket",
                    "S3Prefix": "exports/"
                },
                "Status": "active",
                "StatusMessage": "updating"
            }
        ]
    }

Output for an export image task that is completed. The resulting image file in Amazon S3 is ``my-export-bucket/exports/export-ami-1234567890abcdef0.vmdk``. ::

    {
        "ExportImageTasks": [
            {
                "ExportImageTaskId": "export-ami-1234567890abcdef0"
                "S3ExportLocation": {
                    "S3Bucket": "my-export-bucket",
                    "S3Prefix": "exports/"
                },
                "Status": "completed"
            }
        ]
    }
