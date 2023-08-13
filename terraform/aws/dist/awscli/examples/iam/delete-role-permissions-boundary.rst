**To delete a permissions boundary from an IAM role**

The following ``delete-role-permissions-boundary`` example deletes the permissions boundary for the specified IAM role. To apply a permissions boundary to a role, use the ``put-role-permissions-boundary`` command. ::

    aws iam delete-role-permissions-boundary \
        --role-name lambda-application-role

This command produces no output.
