**To list all members in the current region**

The following ``list-members`` example lists all member accounts and their details for the current region. ::

    aws guardduty list-members \
        --detector-id 12abc34d567e8fa901bc2d34eexample 

Output::
    
    {
        "Members": [
            {
                "RelationshipStatus": "Enabled",
                "InvitedAt": "2020-06-09T22:49:00.910Z",
                "MasterId": "123456789111",
                "DetectorId": "7ab8b2f61b256c87f793f6a86example",
                "UpdatedAt": "2020-06-09T23:08:22.512Z",
                "Email": "your+member@example.com",
                "AccountId": "123456789222"
            }
        ]
    }

For more information, see `Understanding the Relationship between GuardDuty Master and Member Accounts <https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_accounts.html#master_member_relationships>`__ in the GuardDuty User Guide.