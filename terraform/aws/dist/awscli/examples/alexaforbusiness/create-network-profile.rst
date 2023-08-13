**To create a network profile**

The following ``create-network-profile`` example creates a network profile with the specified details. ::

    aws alexaforbusiness create-network-profile \
        --network-profile-name Network123 \
        --ssid Janenetwork \
        --security-type WPA2_PSK \
        --current-password 12345

Output::

    {
        "NetworkProfileArn": "arn:aws:a4b:us-east-1:123456789012:network-profile/a1b2c3d4-5678-90ab-cdef-EXAMPLE11111/a1b2c3d4-5678-90ab-cdef-EXAMPLE22222"
    }            

For more information, see `Managing Network Profiles <https://docs.aws.amazon.com/a4b/latest/ag/manage-network-profiles.html>`__ in the *Alexa for Business Administration Guide*.
