**Example 1: To modify an instance's capacity reservation targeting settings**

The following ``modify-instance-capacity-reservation-attributes`` example modifies a stopped instance to target a specific capacity reservation. ::

    aws ec2 modify-instance-capacity-reservation-attributes \
        --instance-id i-EXAMPLE8765abcd4e \
        --capacity-reservation-specification 'CapacityReservationTarget={CapacityReservationId= cr-1234abcd56EXAMPLE }'

Output::

    {
        "Return": true
    }

**Example 2: To modify an instance's capacity reservation targeting settings**

The following ``modify-instance-capacity-reservation-attributes`` example modifies a stopped instance that targets the specified capacity reservation to launch in any capacity reservation that has matching attributes (instance type, platform, Availability Zone) and that has open instance matching criteria. ::

    aws ec2 modify-instance-capacity-reservation-attributes \
        --instance-id i-EXAMPLE8765abcd4e \
        --capacity-reservation-specification 'CapacityReservationPreference=open'

Output::

    {
        "Return": true
    }

For more information, see `Modifying an Instance's Capacity Reservation Settings <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/capacity-reservations-using.html#capacity-reservations-modify-instance>`__ in the *Amazon Elastic Compute Cloud User Guide for Linux Instances*.
