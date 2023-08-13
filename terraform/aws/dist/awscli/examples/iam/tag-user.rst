**To add a tag to a user**

The following ``tag-user`` command adds a tag with the associated Department to the specified user. This command produces no output. ::

    aws iam tag-user --user-name alice --tags '{"Key": "Department", "Value": "Accounting"}'

For more information, see `Tagging IAM Entities`_ in the *AWS IAM User Guide*

.. _`Tagging IAM Entities`: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_tags.html
