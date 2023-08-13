**Example 1: To describe one or more of your capacity reservations**

The following ``describe-capacity-reservations`` example displays details about all of your capacity reservations in the current AWS Region. ::

    aws ec2 describe-capacity-reservations

Output::

    {
        "CapacityReservations": [
            {
                "CapacityReservationId": "cr-1234abcd56EXAMPLE ",
                "EndDateType": "unlimited",
                "AvailabilityZone": "eu-west-1a",
                "InstanceMatchCriteria": "open",
                "Tags": [],
                "EphemeralStorage": false,
                "CreateDate": "2019-08-16T09:03:18.000Z",
                "AvailableInstanceCount": 1,
                "InstancePlatform": "Linux/UNIX",
                "TotalInstanceCount": 1,
                "State": "active",
                "Tenancy": "default",
                "EbsOptimized": true,
                "InstanceType": "a1.medium"
            },
            {
                "CapacityReservationId": "cr-abcdEXAMPLE9876ef ",
                "EndDateType": "unlimited",
                "AvailabilityZone": "eu-west-1a",
                "InstanceMatchCriteria": "open",
                "Tags": [],
                "EphemeralStorage": false,
                "CreateDate": "2019-08-07T11:34:19.000Z",
                "AvailableInstanceCount": 3,
                "InstancePlatform": "Linux/UNIX",
                "TotalInstanceCount": 3,
                "State": "cancelled",
                "Tenancy": "default",
                "EbsOptimized": true,
                "InstanceType": "m5.large"
            }
        ]
    }

**Example 2: To describe one or more of your capacity reservations**

The following ``describe-capacity-reservations`` example displays details about the specified capacity reservation. ::

    aws ec2 describe-capacity-reservations \
        --capacity-reservation-id cr-1234abcd56EXAMPLE

Output::

    {
        "CapacityReservations": [
            {
                "CapacityReservationId": "cr-1234abcd56EXAMPLE",
                "EndDateType": "unlimited",
                "AvailabilityZone": "eu-west-1a",
                "InstanceMatchCriteria": "open",
                "Tags": [],
                "EphemeralStorage": false,
                "CreateDate": "2019-08-16T09:03:18.000Z",
                "AvailableInstanceCount": 1,
                "InstancePlatform": "Linux/UNIX",
                "TotalInstanceCount": 1,
                "State": "active",
                "Tenancy": "default",
                "EbsOptimized": true,
                "InstanceType": "a1.medium"
            }
        ]
    }

For more information, see `Viewing a Capacity Reservation <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/capacity-reservations-using.html#capacity-reservations-view>`__ in the *Amazon Elastic Compute Cloud User Guide for Linux Instances*.