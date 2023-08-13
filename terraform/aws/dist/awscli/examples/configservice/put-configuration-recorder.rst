**To record all supported resources**

The following command creates a configuration recorder that tracks changes to all supported resource types, including global resource types::

    aws configservice put-configuration-recorder --configuration-recorder name=default,roleARN=arn:aws:iam::123456789012:role/config-role --recording-group allSupported=true,includeGlobalResourceTypes=true

**To record specific types of resources**

The following command creates a configuration recorder that tracks changes to only those types of resources that are specified in the JSON file for the `--recording-group` option::

    aws configservice put-configuration-recorder --configuration-recorder name=default,roleARN=arn:aws:iam::123456789012:role/config-role --recording-group file://recordingGroup.json

`recordingGroup.json` is a JSON file that specifies the types of resources that AWS Config will record::

    {
      "allSupported": false,
      "includeGlobalResourceTypes": false,
      "resourceTypes": [
        "AWS::EC2::EIP",
        "AWS::EC2::Instance",
        "AWS::EC2::NetworkAcl",
        "AWS::EC2::SecurityGroup",
        "AWS::CloudTrail::Trail",
        "AWS::EC2::Volume",
        "AWS::EC2::VPC",
        "AWS::IAM::User",
        "AWS::IAM::Policy"
      ]
    }

Before you can specify resource types for the `resourceTypes` key, you must set the `allSupported` and `includeGlobalResourceTypes` options to false or omit them.

If the command succeeds, AWS Config returns no output. To verify the settings of your configuration recorder, run the `describe-configuration-recorders`__ command.

.. __: http://docs.aws.amazon.com/cli/latest/reference/configservice/describe-configuration-recorders.html