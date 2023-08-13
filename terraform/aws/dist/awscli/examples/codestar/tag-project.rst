**To attach a tag to a project**

The following ``tag-project`` example adds a tag named ``Department`` and a value of ``Marketing`` to the specified project. ::

    aws codestar tag-project \
        --id my-project \
        --tags Department=Marketing

Output::

    {
        "tags": {
            "Department": "Marketing"
        }
    }
