**To describe your Elastic Load Balancing limits**

The following ``describe-account-limits`` example displays the Elastic Load Balancing limits for your AWS account in the current Region. ::

    aws elbv2 describe-account-limits

Output::

    {
        "Limits": [
          {
              "Name": "application-load-balancers",
              "Max": "20"
          },
          {
              "Name": "target-groups",
              "Max": "3000"
          },
          {
              "Name": "targets-per-application-load-balancer",
              "Max": "1000"
          },
          {
              "Name": "listeners-per-application-load-balancer",
              "Max": "50"
          },
          {
              "Name": "rules-per-application-load-balancer",
              "Max": "100"
          },
          {
              "Name": "network-load-balancers",
              "Max": "20"
          },
          {
              "Name": "targets-per-network-load-balancer",
              "Max": "3000"
          },
          {
              "Name": "targets-per-availability-zone-per-network-load-balancer",
              "Max": "500"
          },
          {
              "Name": "listeners-per-network-load-balancer",
              "Max": "50"
          },
          {
              "Name": "condition-values-per-alb-rule",
              "Max": "5"
          },
          {
              "Name": "condition-wildcards-per-alb-rule",
              "Max": "5"
          }
        ]
    }
