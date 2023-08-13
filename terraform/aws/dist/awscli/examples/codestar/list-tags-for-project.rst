**To view tags for a project**

The following ``list-tags-for-project`` example retrieves the tags attached to the specified project. ::

    aws codestar list-tags-for-project \
        --id my-project

Output::

    {
        "tags": {
            "Department": "Marketing",
            "Team": "Website"
        }
    }
