**To search network profiles**

The following ``search-network-profiles`` example lists network profiles that meet a set of filter and sort criteria. In this example, all profiles are listed. ::

    aws alexaforbusiness search-network-profiles

Output::

    {
        "NetworkProfiles": [
            {
                "NetworkProfileArn": "arn:aws:a4b:us-east-1:123456789111:network-profile/a1b2c3d4-5678-90ab-cdef-EXAMPLE22222/a1b2c3d4-5678-90ab-cdef-EXAMPLE33333",
                "NetworkProfileName": "Networkprofile1",
                "Description": "Personal network",
                "Ssid": "Janenetwork",
                "SecurityType": "WPA2_PSK"
            },
            {
                "NetworkProfileArn": "arn:aws:a4b:us-east-1:123456789222:network-profile/a1b2c3d4-5678-90ab-cdef-EXAMPLE44444/a1b2c3d4-5678-90ab-cdef-EXAMPLE55555",
                "NetworkProfileName": "Networkprofile2",
                "Ssid": "Johnnetwork",
                "SecurityType": "WPA2_PSK"
            },
            {
                "NetworkProfileArn": "arn:aws:a4b:us-east-1:123456789333:network-profile/a1b2c3d4-5678-90ab-cdef-EXAMPLE66666/a1b2c3d4-5678-90ab-cdef-EXAMPLE77777",
                "NetworkProfileName": "Networkprofile3",
                "Ssid": "Carlosnetwork",
                "SecurityType": "WPA2_PSK"
            }
        ],
        "TotalCount": 3
    }         

For more information, see `Managing Network Profiles <https://docs.aws.amazon.com/a4b/latest/ag/manage-network-profiles.html>`__ in the *Alexa for Business Administration Guide*.
