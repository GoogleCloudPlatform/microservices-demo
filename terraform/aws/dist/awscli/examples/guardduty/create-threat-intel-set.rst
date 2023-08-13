**To create a new threat intel set in the current region.**

This example shows how to upload a threat intel set to GuardDuty and activate it immediately. ::

    aws guardduty create-threat-intel-set \
        --detector-id b6b992d6d2f48e64bc59180bfexample \
        --name myThreatSet \
        --format TXT \
        --location s3://EXAMPLEBUCKET/threatlist.csv \
        --activate 

Output::

    {
        "ThreatIntelSetId": "20b9a4691aeb33506b808878cexample"
    }

For more information, see `Trusted IP and threat lists <https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_upload_lists.html>`__ in the *GuardDuty User Guide*.
