**To remove a tag from a user**

The following ``untag-user`` command removes any tag with the key name 'Department' from the specified user. This command produces no output. ::

    aws iam untag-user --user-name alice --tag-keys Department

For more information, see `Tagging IAM Entities`_ in the *AWS IAM User Guide*

.. _`Tagging IAM Entities`: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_tags.html
