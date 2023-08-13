**To describe stacks**

The following ``describe-stacks`` command describes an account's stacks. ::

  aws opsworks --region us-east-1 describe-stacks

*Output*::

  {
    "Stacks": [
      {
        "ServiceRoleArn": "arn:aws:iam::444455556666:role/aws-opsworks-service-role",
        "StackId": "aeb7523e-7c8b-49d4-b866-03aae9d4fbcb",
        "DefaultRootDeviceType": "instance-store",
        "Name": "TomStack-sd",
        "ConfigurationManager": {
          "Version": "11.4",
          "Name": "Chef"
        },
        "UseCustomCookbooks": true,
        "CustomJson": "{\n  \"tomcat\": {\n    \"base_version\": 7,\n    \"java_opts\": \"-Djava.awt.headless=true -Xmx256m\"\n  },\n  \"datasources\": {\n    \"ROOT\": \"jdbc/mydb\"\n  }\n}",
        "Region": "us-east-1",
        "DefaultInstanceProfileArn": "arn:aws:iam::444455556666:instance-profile/aws-opsworks-ec2-role",
        "CustomCookbooksSource": {
          "Url": "git://github.com/example-repo/tomcustom.git",
          "Type": "git"
        },
        "DefaultAvailabilityZone": "us-east-1a",
        "HostnameTheme": "Layer_Dependent",
        "Attributes": {
          "Color": "rgb(45, 114, 184)"
        },
        "DefaultOs": "Amazon Linux",
        "CreatedAt": "2013-08-01T22:53:42+00:00"
      },
      {
        "ServiceRoleArn": "arn:aws:iam::444455556666:role/aws-opsworks-service-role",
        "StackId": "40738975-da59-4c5b-9789-3e422f2cf099",
        "DefaultRootDeviceType": "instance-store",
        "Name": "MyStack",
        "ConfigurationManager": {
          "Version": "11.4",
          "Name": "Chef"
        },
        "UseCustomCookbooks": false,
        "Region": "us-east-1",
        "DefaultInstanceProfileArn": "arn:aws:iam::444455556666:instance-profile/aws-opsworks-ec2-role",
        "CustomCookbooksSource": {},
        "DefaultAvailabilityZone": "us-east-1a",
        "HostnameTheme": "Layer_Dependent",
        "Attributes": {
          "Color": "rgb(45, 114, 184)"
        },
        "DefaultOs": "Amazon Linux",
        "CreatedAt": "2013-10-25T19:24:30+00:00"
      }
    ]
  }

**More Information**

For more information, see `Stacks`_ in the *AWS OpsWorks User Guide*.

.. _`Stacks`: http://docs.aws.amazon.com/opsworks/latest/userguide/workingstacks.html

