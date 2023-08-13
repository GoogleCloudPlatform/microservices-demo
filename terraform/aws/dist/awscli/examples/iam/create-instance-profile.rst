**To create an instance profile**

The following ``create-instance-profile`` command creates an instance profile named ``Webserver``::

  aws iam create-instance-profile --instance-profile-name Webserver

Output::

  {
      "InstanceProfile": {
          "InstanceProfileId": "AIPAJMBYC7DLSPEXAMPLE",
          "Roles": [],
          "CreateDate": "2015-03-09T20:33:19.626Z",
          "InstanceProfileName": "Webserver",
          "Path": "/",
          "Arn": "arn:aws:iam::123456789012:instance-profile/Webserver"
      }
  }

To add a role to an instance profile, use the ``add-role-to-instance-profile`` command.

For more information, see `Using IAM Roles to Delegate Permissions to Applications that Run on Amazon EC2`_ in the *Using IAM* guide.

.. _`Using IAM Roles to Delegate Permissions to Applications that Run on Amazon EC2`: http://docs.aws.amazon.com/IAM/latest/UserGuide/roles-usingrole-ec2instance.html