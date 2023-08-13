**To create a Traffic Mirror Filter**

The following ``create-traffic-mirror-filter`` example creates a Traffic Mirror filter. After you create the filter, use ``create-traffic-mirror-filter-rule`` to add rules to the filter. ::

    aws ec2 create-traffic-mirror-filter \
        --description "TCP Filter"

Output::

    {        "ClientToken": "28908518-100b-4987-8233-8c744EXAMPLE",        "TrafficMirrorFilter": {            "TrafficMirrorFilterId": "tmf-04812ff784EXAMPLE",            "Description": "TCP Filter",            "EgressFilterRules": [],            "IngressFilterRules": [],            "Tags": [],            "NetworkServices": []        }    }

For more information, see `Create a Traffic Mirror Filter <https://docs.aws.amazon.com/vpc/latest/mirroring/traffic-mirroring-filter.html#create-traffic-mirroring-filter>`__ in the *AWS Traffic Mirroring Guide*.
