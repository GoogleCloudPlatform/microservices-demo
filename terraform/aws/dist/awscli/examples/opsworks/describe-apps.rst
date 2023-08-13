**To describe apps**

The following ``describe-apps`` command describes the apps in a specified stack.  ::

  aws opsworks --region us-east-1 describe-apps --stack-id 38ee91e2-abdc-4208-a107-0b7168b3cc7a

*Output*: This particular stack has one app.

::

  {
    "Apps": [
      {
        "StackId": "38ee91e2-abdc-4208-a107-0b7168b3cc7a",
        "AppSource": {
          "Url": "https://s3-us-west-2.amazonaws.com/opsworks-tomcat/simplejsp.zip",
          "Type": "archive"
        },
        "Name": "SimpleJSP",
        "EnableSsl": false,
        "SslConfiguration": {},
        "AppId": "da1decc1-0dff-43ea-ad7c-bb667cd87c8b",
        "Attributes": {
          "RailsEnv": null,
          "AutoBundleOnDeploy": "true",
          "DocumentRoot": "ROOT"
        },
        "Shortname": "simplejsp",
        "Type": "other",
        "CreatedAt": "2013-08-01T21:46:54+00:00"
      }
    ]
  }

**More Information**

For more information, see Apps_ in the *AWS OpsWorks User Guide*.

.. _Apps: http://docs.aws.amazon.com/opsworks/latest/userguide/workingapps.html

