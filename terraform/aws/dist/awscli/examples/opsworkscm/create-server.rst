**To create a server**

The following ``create-server`` example creates a new Chef Automate server named ``automate-06`` in your default region. Note that defaults are used for most other settings, such as number of backups to retain, and maintenance and backup start times. Before you run a ``create-server`` command, complete prerequisites in `Getting Started with AWS OpsWorks for Chef Automate <https://docs.aws.amazon.com/opsworks/latest/userguide/gettingstarted-opscm.html>`__ in the *AWS Opsworks for Chef Automate User Guide*. ::

    aws opsworks-cm create-server \
        --engine "Chef" \
        --engine-model "Single" \
        --engine-version "12" \
        --server-name "automate-06" \
        --instance-profile-arn "arn:aws:iam::1019881987024:instance-profile/aws-opsworks-cm-ec2-role" \
        --instance-type "t2.medium" \
        --key-pair "amazon-test" \
        --service-role-arn "arn:aws:iam::044726508045:role/aws-opsworks-cm-service-role"

The output shows you information similar to the following about the new server::

    {
        "Server": { 
            "BackupRetentionCount": 10,
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
            "InstanceProfileArn": "arn:aws:iam::1019881987024:instance-profile/aws-opsworks-cm-ec2-role",
            "InstanceType": "t2.medium",
            "KeyPair": "amazon-test",
            "MaintenanceStatus": "",
            "PreferredBackupWindow": "Sun:02:00",
            "PreferredMaintenanceWindow": "00:00",
            "SecurityGroupIds": [ "sg-1a24c270" ],
            "ServerArn": "arn:aws:iam::1019881987024:instance/automate-06-1010V4UU2WRM2",
            "ServerName": "automate-06",
            "ServiceRoleArn": "arn:aws:iam::1019881987024:role/aws-opsworks-cm-service-role",
            "Status": "CREATING",
            "StatusReason": "",
            "SubnetIds": [ "subnet-49436a18" ]
        }
    }

For more information, see `UpdateServer <https://docs.aws.amazon.com/opsworks-cm/latest/APIReference/API_UpdateServer.html>`_ in the *AWS OpsWorks for Chef Automate API Reference*.