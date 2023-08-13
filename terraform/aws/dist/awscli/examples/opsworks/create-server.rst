**To create a server**

The following ``create-server`` example creates a new Chef Automate server named ``automate-06`` in your default region. Note that defaults are used for most other settings, such as number of backups to retain, and maintenance and backup start times. Before you run a ``create-server`` command, complete prerequisites in `Getting Started with AWS OpsWorks for Chef Automate <https://docs.aws.amazon.com/opsworks/latest/userguide/gettingstarted-opscm.html>`__ in the *AWS Opsworks for Chef Automate User Guide*. ::

    aws opsworks-cm create-server \
        --engine "ChefAutomate" \
        --instance-profile-arn "arn:aws:iam::012345678901:instance-profile/aws-opsworks-cm-ec2-role" \
        --instance-type "t2.medium" \
        --server-name "automate-06" \
        --service-role-arn "arn:aws:iam::012345678901:role/aws-opsworks-cm-service-role"

Output::

    {
        "Server": {
            "AssociatePublicIpAddress": true,
            "BackupRetentionCount": 10,
            "CreatedAt": 2019-12-29T13:38:47.520Z,
            "DisableAutomatedBackup": FALSE,
            "Endpoint": "https://opsworks-cm.us-east-1.amazonaws.com",
            "Engine": "ChefAutomate",
            "EngineAttributes": [
                {
                    "Name": "CHEF_AUTOMATE_ADMIN_PASSWORD",
                    "Value": "1Example1"
                }
            ],
            "EngineModel": "Single",
            "EngineVersion": "2019-08",
            "InstanceProfileArn": "arn:aws:iam::012345678901:instance-profile/aws-opsworks-cm-ec2-role",
            "InstanceType": "t2.medium",
            "PreferredBackupWindow": "Sun:02:00",
            "PreferredMaintenanceWindow": "00:00",
            "SecurityGroupIds": [ "sg-12345678" ],
            "ServerArn": "arn:aws:iam::012345678901:instance/automate-06-1010V4UU2WRM2",
            "ServerName": "automate-06",
            "ServiceRoleArn": "arn:aws:iam::012345678901:role/aws-opsworks-cm-service-role",
            "Status": "CREATING",
            "SubnetIds": [ "subnet-12345678" ]
        }
    }

For more information, see `CreateServer <https://docs.aws.amazon.com/opsworks-cm/latest/APIReference/API_CreateServer.html>`__ in the *AWS OpsWorks for Chef Automate API Reference*.