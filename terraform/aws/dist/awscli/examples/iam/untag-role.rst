**To remove a tag from a role**

The following ``untag-role`` command removes any tag with the key name 'Department' from the specified role. This command produces no output. ::

    aws iam untag-role --role-name my-role --tag-keys Department

For more information, see `Tagging IAM Entities`_ in the *AWS IAM User Guide*

.. _`Tagging IAM Entities`: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_tags.html
