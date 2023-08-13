**To disassociate from your current master account in the current region**

The following ``disassociate-from-master-account`` example dissassociates your account from the current GuardDuty master account in the current AWS region. ::

    aws guardduty disassociate-from-master-account \
        --detector-id d4b040365221be2b54a6264dcexample 

This command produces no output.

For more information, see `Understanding the Relationship between GuardDuty Master and Member Accounts <https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_accounts.html#master_member_relationships>`__ in the GuardDuty User Guide.