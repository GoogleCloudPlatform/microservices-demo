**To delete a user profile**

The following ``delete-user-profile`` example deletes the user profile for the user with the specified ARN. ::

    aws codestar delete-user-profile \
        --user-arn arn:aws:iam::123456789012:user/intern

Output::

    {
        "userArn": "arn:aws:iam::123456789012:user/intern"
    }
