**To create backups**

The following ``create-backup`` command starts a manual backup of a Chef Automate server
named ``automate-06`` in the ``us-east-1`` region. The command adds a descriptive message to
the backup in the ``--description`` parameter.::

  aws opsworks-cm create-backup --server-name 'automate-06' --description "state of my infrastructure at launch"

The output shows you information similar to the following about the new backup.
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
         "Status": "OK",
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

