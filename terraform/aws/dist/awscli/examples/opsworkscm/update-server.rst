**To update a server**

The following ``update-server`` command updates the maintenance start time of the specified Chef Automate server in your default region. The ``--preferred-maintenance-window`` parameter is added to change the start day and time of server maintenance to Mondays at 9:15 a.m. UTC.::

    aws opsworks-cm update-server \
        --server-name "automate-06" \
        --preferred-maintenance-window "Mon:09:15"

The output shows you information similar to the following about the updated server. ::

    {
        "Server": { 
            "BackupRetentionCount": 8,
            "CreatedAt": 2016-07-29T13:38:47.520Z,
            "DisableAutomatedBackup": TRUE,
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
            "MaintenanceStatus": "OK",
            "PreferredBackupWindow": "Mon:09:15",
            "PreferredMaintenanceWindow": "03:00",
            "SecurityGroupIds": [ "sg-1a24c270" ],
            "ServerArn": "arn:aws:iam::1019881987024:instance/automate-06-1010V4UU2WRM2",
            "ServerName": "automate-06",
            "ServiceRoleArn": "arn:aws:iam::1019881987024:role/aws-opsworks-cm-service-role.1114810729735",
            "Status": "HEALTHY",
            "StatusReason": "",
            "SubnetIds": [ "subnet-49436a18" ]
        }
    }

For more information, see `UpdateServer <https://docs.aws.amazon.com/opsworks-cm/latest/APIReference/API_UpdateServer.html>`_ in the *AWS OpsWorks for Chef Automate API Reference*.
