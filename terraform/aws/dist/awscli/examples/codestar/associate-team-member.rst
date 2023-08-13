**To add a team member to a project**

The following ``associate-team-member`` example makes the ``intern`` user a viewer on the project with the specified ID. ::

    aws codestar associate-team-member \
        --project-id my-project \
        --user-arn arn:aws:iam::123456789012:user/intern \
        --project-role Viewer

This command produces no output.
