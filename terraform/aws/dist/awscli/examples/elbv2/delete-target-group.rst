**To delete a target group**

The following ``delete-target-group`` example deletes the specified target group. ::

    aws elbv2 delete-target-group \
        --target-group-arn arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-targets/73e2d6bc24d8a067
