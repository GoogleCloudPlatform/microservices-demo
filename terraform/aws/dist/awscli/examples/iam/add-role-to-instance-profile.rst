**To add a role to an instance profile**

The following ``add-role-to-instance-profile`` command adds the role named ``S3Access`` to the instance profile named ``Webserver``::

  aws iam add-role-to-instance-profile --role-name S3Access --instance-profile-name Webserver

To create an instance profile, use the ``create-instance-profile`` command.

For more information, see `Using IAM Roles to Delegate Permissions to Applications that Run on Amazon EC2`_ in the *Using IAM* guide.

.. _`Using IAM Roles to Delegate Permissions to Applications that Run on Amazon EC2`: http://docs.aws.amazon.com/IAM/latest/UserGuide/roles-usingrole-ec2instance.html