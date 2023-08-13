**To create a timeline event**

The following ``create-timeline-event`` example creates a custom timeline event at the specified time on the specified incident. ::

    aws ssm-incidents create-timeline-event \
        --event-data "\"example timeline event\"" \
        --event-time 2020-10-01T20:30:00.000 \
        --event-type "Custom Event" \
        --incident-record-arn "arn:aws:ssm-incidents::111122223333:incident-record/Example-Response-Plan/6ebcc812-85f5-b7eb-8b2f-283e4d844308"

Output::

    {
        "eventId": "c0bcc885-a41d-eb01-b4ab-9d2de193643c",
        "incidentRecordArn": "arn:aws:ssm-incidents::111122223333:incident-record/Example-Response-Plan/6ebcc812-85f5-b7eb-8b2f-283e4d844308"
    }

For more information, see `Incident details <https://docs.aws.amazon.com/incident-manager/latest/userguide/tracking-details.html>`__ in the *Incident Manager User Guide*.