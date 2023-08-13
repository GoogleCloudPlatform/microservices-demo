**To list the available widgets**

The following ``list-studio-members`` example lists the available studio members in your AWS account. ::

    aws nimble list-studio-members \
        --studio-id "StudioID"

Output::

    {
        "members": [
            {
                "identityStoreId": "d-EXAMPLE11111",
                "persona": "ADMINISTRATOR",
                "principalId": "EXAMPLE11111-e9fd012a-94ad-4f16-9866-c69a63ab6486"
            }
        ]
    }

For more information, see `Adding studio users <https://docs.aws.amazon.com/nimble-studio/latest/userguide/adding-studio-users.html>`__ in the *Amazon Nimble Studio User Guide*.