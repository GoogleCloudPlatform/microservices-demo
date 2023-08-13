**To remove a team member**

The following ``disassociate-team-member`` example removes the user with the specified ARN from the project ``my-project``. ::

    aws codestar disassociate-team-member \
        --project-id my-project \
        --user-arn arn:aws:iam::123456789012:user/intern

This command produces no output.
