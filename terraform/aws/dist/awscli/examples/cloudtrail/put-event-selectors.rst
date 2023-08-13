**To configure event selectors for a trail**

To create an event selector, run the ''put-event-selectors'' command. When an event occurs in your account, CloudTrail evaluates 
the configuration for your trails. If the event matches any event selector for a trail, the trail processes and logs the event. 
You can configure up to 5 event selectors for a trail and up to 250 data resources for a trail.

The following example creates an event selector for a trail named ''TrailName'' to include read-only and write-only management events, 
data events for two Amazon S3 bucket/prefix combinations, and data events for a single AWS Lambda function named ''hello-world-python-function''::



  aws cloudtrail put-event-selectors --trail-name TrailName --event-selectors '[{"ReadWriteType": "All","IncludeManagementEvents": true,"DataResources": [{"Type":"AWS::S3::Object", "Values": ["arn:aws:s3:::mybucket/prefix","arn:aws:s3:::mybucket2/prefix2"]},{"Type": "AWS::Lambda::Function","Values": ["arn:aws:lambda:us-west-2:999999999999:function:hello-world-python-function"]}]}]'

Output::

  {
    "EventSelectors": [
        {
            "IncludeManagementEvents": true,
            "DataResources": [
                {
                    "Values": [
                        "arn:aws:s3:::mybucket/prefix",
                        "arn:aws:s3:::mybucket2/prefix2"
                    ],
                    "Type": "AWS::S3::Object"
                },
                {
                    "Values": [
                        "arn:aws:lambda:us-west-2:123456789012:function:hello-world-python-function"
                    ],
                    "Type": "AWS::Lambda::Function"
                },
            ],
            "ReadWriteType": "All"
        }
    ],
    "TrailARN": "arn:aws:cloudtrail:us-east-2:123456789012:trail/TrailName"
  }

The following example creates an event selector for a trail named ''TrailName2'' that includes all events, including read-only and write-only management events, and all data events for all Amazon S3 buckets and AWS Lambda functions in the AWS account::

  aws cloudtrail put-event-selectors --trail-name TrailName2 --event-selectors '[{"ReadWriteType": "All","IncludeManagementEvents": true,"DataResources": [{"Type":"AWS::S3::Object", "Values": ["arn:aws:s3:::"]},{"Type": "AWS::Lambda::Function","Values": ["arn:aws:lambda"]}]}]'

Output::

  {
    "EventSelectors": [
        {
            "IncludeManagementEvents": true,
            "DataResources": [
                {
                    "Values": [
                        "arn:aws:s3:::"
                    ],
                    "Type": "AWS::S3::Object"
                },
                {
                    "Values": [
                        "arn:aws:lambda"
                    ],
                    "Type": "AWS::Lambda::Function"
                },
            ],
            "ReadWriteType": "All"
        }
    ],
    "TrailARN": "arn:aws:cloudtrail:us-east-2:123456789012:trail/TrailName2"
  }
  