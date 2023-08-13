The following command describes a log group named ``my-logs``::

  aws logs describe-log-groups --log-group-name-prefix my-logs

Output::

  {
      "logGroups": [
          {
              "storedBytes": 0,
              "metricFilterCount": 0,
              "creationTime": 1433189500783,
              "logGroupName": "my-logs",
              "retentionInDays": 5,
              "arn": "arn:aws:logs:us-west-2:0123456789012:log-group:my-logs:*"
          }
      ]
  }
