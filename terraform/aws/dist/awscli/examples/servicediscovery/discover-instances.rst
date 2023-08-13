**To discover registered instances**

The following ``discover-instances`` example discovers registered instances. ::

    aws servicediscovery discover-instances \
        --namespace-name example.com \
        --service-name myservice \
        --max-results 10 \
        --health-status ALL

Output::

    {
        "Instances": [
            {
                "InstanceId": "myservice-53",
                "NamespaceName": "example.com",
                "ServiceName": "myservice",
                "HealthStatus": "UNKNOWN",
                "Attributes": {
                    "AWS_INSTANCE_IPV4": "172.2.1.3",
                    "AWS_INSTANCE_PORT": "808"
                }
            }
        ]
    }

