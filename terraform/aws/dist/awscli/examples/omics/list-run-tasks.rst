**To get a list of tasks**

The following ``list-run-tasks`` example gets a list of tasks for a workflow run. ::

    aws omics list-run-tasks \
        --id 1234567

Output::

    {
        "items": [
            {
                "cpus": 1,
                "creationTime": "2022-11-30T23:13:00.718651Z",
                "memory": 15,
                "name": "CramToBamTask",
                "startTime": "2022-11-30T23:17:47.016Z",
                "status": "COMPLETED",
                "stopTime": "2022-11-30T23:18:21.503Z",
                "taskId": "1234567"
            },
            {
                "cpus": 1,
                "creationTime": "2022-11-30T23:18:32.315606Z",
                "memory": 4,
                "name": "ValidateSamFile",
                "startTime": "2022-11-30T23:23:40.165Z",
                "status": "COMPLETED",
                "stopTime": "2022-11-30T23:24:14.766Z",
                "taskId": "1234567"
            }
        ]
    }

For more information, see `Omics Workflows <https://docs.aws.amazon.com/omics/latest/dev/workflows.html>`__ in the *Amazon Omics Developer Guide*.
