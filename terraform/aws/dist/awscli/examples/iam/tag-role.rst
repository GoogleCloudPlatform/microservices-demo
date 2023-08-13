**To add a tag to a role**

The following ``tag-role`` command adds a tag with a Department name to the specified role. This command produces no output. ::

    aws iam tag-role --role-name my-role --tags '{"Key": "Department", "Value": "Accounting"}'

For more information, see `Tagging IAM Entities`_ in the *AWS IAM User Guide*

.. _`Tagging IAM Entities`: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_tags.html
