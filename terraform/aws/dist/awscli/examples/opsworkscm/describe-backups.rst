**To describe backups**

The following ``describe-backups`` command returns information about all backups
associated with your account in your default region.::

  aws opsworks-cm describe-backups

The output for each backup entry returned by the command resembles the following.
*Output*::

  {
   "Backups": [ 
      { 
         "BackupArn": "string",
         "BackupId": "automate-06-20160729133847520",
         "BackupType": "MANUAL",
         "CreatedAt": 2016-07-29T13:38:47.520Z,
         "Description": "state of my infrastructure at launch",
         "Engine": "Chef",
         "EngineModel": "Single",
         "EngineVersion": "12",
         "InstanceProfileArn": "arn:aws:iam::1019881987024:instance-profile/automate-06-1010V4UU2WRM2",
         "InstanceType": "m4.large",
         "KeyPair": "",
         "PreferredBackupWindow": "",
         "PreferredMaintenanceWindow": "",
         "S3LogUrl": "https://s3.amazonaws.com/automate-06/automate-06-20160729133847520",
         "SecurityGroupIds": [ "sg-1a24c270" ],
         "ServerName": "automate-06",
         "ServiceRoleArn": "arn:aws:iam::1019881987024:role/aws-opsworks-cm-service-role.1114810729735",
         "Status": "Successful",
         "StatusDescription": "",
         "SubnetIds": [ "subnet-49436a18" ],
         "ToolsVersion": "string",
         "UserArn": "arn:aws:iam::1019881987024:user/opsworks-user"
      }
   ],
  }

**More Information**

For more information, see `Back Up and Restore an AWS OpsWorks for Chef Automate Server`_ in the *AWS OpsWorks User Guide*.

.. _`Back Up and Restore an AWS OpsWorks for Chef Automate Server`: http://docs.aws.amazon.com/opsworks/latest/userguide/opscm-backup-restore.html

