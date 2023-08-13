**To start maintenance**

The following ``start-maintenance`` example manually starts maintenance on the specified Chef Automate or Puppet Enterprise server in your default region. This command is useful if an earlier, automated maintenance attempt failed, and the underlying cause of maintenance failure has been resolved. ::

    aws opsworks-cm start-maintenance \
        --server-name 'automate-06'

Output::

    {
        "Server": {
            "AssociatePublicIpAddress": true,
            "BackupRetentionCount": 10,
            "ServerName": "automate-06",
            "CreatedAt": 1569229584.842,
            "CloudFormationStackArn": "arn:aws:cloudformation:us-west-2:123456789012:stack/aws-opsworks-cm-instance-automate-06-1606611794746/EXAMPLE0-31de-11eb-bdb0-0a5b0a1353b8",
            "DisableAutomatedBackup": false,
            "Endpoint": "automate-06-EXAMPLEvr8gjfk5f.us-west-2.opsworks-cm.io",
            "Engine": "ChefAutomate",
            "EngineModel": "Single",
            "EngineAttributes": [],
            "EngineVersion": "2020-07",
            "InstanceProfileArn": "arn:aws:iam::123456789012:instance-profile/aws-opsworks-cm-ec2-role",
            "InstanceType": "m5.large",
            "PreferredMaintenanceWindow": "Sun:01:00",
            "PreferredBackupWindow": "Sun:15:00",
            "SecurityGroupIds": [
                "sg-EXAMPLE"
            ],
            "ServiceRoleArn": "arn:aws:iam::123456789012:role/service-role/aws-opsworks-cm-service-role",
            "Status": "UNDER_MAINTENANCE",
            "SubnetIds": [
                "subnet-EXAMPLE"
            ],
            "ServerArn": "arn:aws:opsworks-cm:us-west-2:123456789012:server/automate-06/0148382d-66b0-4196-8274-d1a2b6dff8d1"
        }
    }

For more information, see `System Maintenance (Puppet Enterprise servers) <https://docs.aws.amazon.com/opsworks/latest/userguide/opspup-maintenance.html>`_ or `System Maintenance (Chef Automate servers) <https://docs.aws.amazon.com/opsworks/latest/userguide/opscm-maintenance.html>`_ in the *AWS OpsWorks User Guide*.