**To create a new filter for the current region**

This example creates a filter that matches all portscan findings for instance created from a specific image.::

    aws guardduty create-filter \
        --detector-id b6b992d6d2f48e64bc59180bfexample \ 
        --action ARCHIVE \
        --name myFilter \
        --finding-criteria '{"Criterion": {"type": {"Eq": ["Recon:EC2/Portscan"]},"resource.instanceDetails.imageId": {"Eq": ["ami-0a7a207083example"]}}}'

Output::

    {
        "Name": "myFilter"
    }

For more information, see `Filtering findings <https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_filter-findings.html>`__ in the *GuardDuty User Guide*.
