**To get network profile details**

The following ``get-network-profile`` example retrieves details of the specified network profile. ::

    aws alexaforbusiness get-network-profile \
        --network-profile-arn arn:aws:a4b:us-east-1:123456789012:network-profile/a1b2c3d4-5678-90ab-cdef-EXAMPLE11111

Output::

    {
        "NetworkProfile": {
            "NetworkProfileArn": "arn:aws:a4b:us-east-1:123456789012:network-profile/a1b2c3d4-5678-90ab-cdef-EXAMPLE11111/a1b2c3d4-5678-90ab-cdef-EXAMPLE22222",
            "NetworkProfileName": "Networkprofile",
            "Ssid": "Janenetwork",
            "SecurityType": "WPA2_PSK",
            "CurrentPassword": "12345"
        }
    }

For more information, see `Managing Network Profiles <https://docs.aws.amazon.com/a4b/latest/ag/manage-network-profiles.html>`__ in the *Alexa for Business Administration Guide*.
