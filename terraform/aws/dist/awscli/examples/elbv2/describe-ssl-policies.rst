**To describe a policy used for SSL negotiation**

The following ``describe-ssl-policies`` example displays details of the specified policy used for SSL negotiation. ::

    aws elbv2 describe-ssl-policies \
        --names ELBSecurityPolicy-2016-08
      
Output::

    {
        "SslPolicies": [
            {
                "SslProtocols": [
                    "TLSv1",
                    "TLSv1.1",
                    "TLSv1.2"
                ],
                "Ciphers": [
                    {
                        "Priority": 1,
                        "Name": "ECDHE-ECDSA-AES128-GCM-SHA256"
                    },
                    {
                        "Priority": 2,
                        "Name": "ECDHE-RSA-AES128-GCM-SHA256"
                    },
                    {
                        "Priority": 3,
                        "Name": "ECDHE-ECDSA-AES128-SHA256"
                    },

                    ...some output truncated...

                    {
                        "Priority": 18,
                        "Name": "AES256-SHA"
                    }
                ],
                "Name": "ELBSecurityPolicy-2016-08"
            }
        ]
    }

**To describe all policies used for SSL negotiation**

The following ``describe-ssl-policies`` example displays details for all the policies that you can use for SSL negotiation. ::

    aws elbv2 describe-ssl-policies
