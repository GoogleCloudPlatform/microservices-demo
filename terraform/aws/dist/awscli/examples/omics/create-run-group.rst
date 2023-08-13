**To create a run group**

The following ``create-run-group`` example creates a run group named ``cram-converter``. ::

    aws omics create-run-group \
        --name cram-converter \
        --max-cpus 20 \
        --max-duration 600

Output::

    {
        "arn": "arn:aws:omics:us-west-2:123456789012:runGroup/1234567",
        "id": "1234567",
        "tags": {}
    }

For more information, see `Omics Workflows <https://docs.aws.amazon.com/omics/latest/dev/workflows.html>`__ in the *Amazon Omics Developer Guide*.
