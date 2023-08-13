**To cancel a capacity reservation**

The following ``cancel-capacity-reservation`` example cancels the specified capacity reservation. ::

    aws ec2 cancel-capacity-reservation \
        --capacity-reservation-id cr-1234abcd56EXAMPLE

Output::

    {
        "Return": true
    }

For more information, see `Canceling a Capacity Reservation <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/capacity-reservations-using.html#capacity-reservations-release>`__ in the *Amazon Elastic Compute Cloud User Guide for Linux Instances*.
