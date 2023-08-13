**To describe servers**

The following ``describe-servers`` command returns information about all servers 
that are associated with your account, and in your default region.::

  aws opsworks-cm describe-servers

The output for each server entry returned by the command resembles the following.
*Output*::

  {
   "Servers": [ 
      { 
         "BackupRetentionCount": 8,
         "CreatedAt": 2016-07-29T13:38:47.520Z,
         "DisableAutomatedBackup": FALSE,
         "Endpoint": "https://opsworks-cm.us-east-1.amazonaws.com",
         "Engine": "Chef",
         "EngineAttributes": [ 
            { 
               "Name": "CHEF_DELIVERY_ADMIN_PASSWORD",
               "Value": "1Password1"
            }
         ],
         "EngineModel": "Single",
         "EngineVersion": "12",
         "InstanceProfileArn": "arn:aws:iam::1019881987024:instance-profile/automate-06-1010V4UU2WRM2",
         "InstanceType": "m4.large",
         "KeyPair": "",
         "MaintenanceStatus": "SUCCESS",
         "PreferredBackupWindow": "03:00",
         "PreferredMaintenanceWindow": "Mon:09:00",
         "SecurityGroupIds": [ "sg-1a24c270" ],
         "ServerArn": "arn:aws:iam::1019881987024:instance/automate-06-1010V4UU2WRM2",
         "ServerName": "automate-06",
         "ServiceRoleArn": "arn:aws:iam::1019881987024:role/aws-opsworks-cm-service-role.1114810729735",
         "Status": "HEALTHY",
         "StatusReason": "",
         "SubnetIds": [ "subnet-49436a18" ]
      }
   ]
  }

**More Information**

For more information, see `DescribeServers`_ in the *AWS OpsWorks for Chef Automate API Guide*.

.. _`DescribeServers`: http://docs.aws.amazon.com/opsworks-cm/latest/APIReference/API_DescribeServers.html
