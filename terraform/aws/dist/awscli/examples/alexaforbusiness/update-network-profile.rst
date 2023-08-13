**To update a network profile**

The following ``update-network-profile`` example updates the specified network profile by using the network profile ARN. ::

    aws alexaforbusiness update-network-profile \
        --network-profile-arn arn:aws:a4b:us-east-1:123456789012:network-profile/a1b2c3d4-5678-90ab-cdef-EXAMPLE11111 \
        --network-profile-name Networkprofile

This command produces no output.         

For more information, see `Managing Network Profiles <https://docs.aws.amazon.com/a4b/latest/ag/manage-network-profiles.html>`__ in the *Alexa for Business Administration Guide*.
