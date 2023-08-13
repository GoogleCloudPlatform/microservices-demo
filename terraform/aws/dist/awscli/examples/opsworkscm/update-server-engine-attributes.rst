**To update server engine attributes**

The following ``update-server-engine-attributes`` command updates the value of the ``CHEF_PIVOTAL_KEY`` engine attribute for a Chef Automate server named ``automate-06``. It is currently not possible to change the value of other engine attributes. ::

    aws opsworks-cm update-server-engine-attributes \
        --attribute-name CHEF_PIVOTAL_KEY \
        --attribute-value "new key value" \
        --server-name "automate-06"

The output shows you information similar to the following about the updated server. ::

    {
        "Server": { 
            "BackupRetentionCount": 2,
            "CreatedAt": 2016-07-29T13:38:47.520Z,
            "DisableAutomatedBackup": FALSE,
            "Endpoint": "https://opsworks-cm.us-east-1.amazonaws.com",
            "Engine": "Chef",
            "EngineAttributes": [ 
                { 
                    "Name": "CHEF_PIVOTAL_KEY",
                    "Value": "new key value"
                }
            ],
            "EngineModel": "Single",
            "EngineVersion": "12",
            "InstanceProfileArn": "arn:aws:iam::1019881987024:instance-profile/automate-06-1010V4UU2WRM2",
            "InstanceType": "m4.large",
            "KeyPair": "",
            "MaintenanceStatus": "SUCCESS",
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

For more information, see `UpdateServerEngineAttributes <https://docs.aws.amazon.com/opsworks-cm/latest/APIReference/API_UpdateServerEngineAttributes.html>`_ in the *AWS OpsWorks for Chef Automate API Reference*.
