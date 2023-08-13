**To modify a DB cluster**

The following ``modify-db-cluster`` example changes the master user password for the DB cluster named ``cluster-2`` and sets the backup retention period to 14 days. The ``--apply-immediately`` parameter causes the changes to be made immediately, instead of waiting until the next maintenance window. ::

    aws rds modify-db-cluster \
        --db-cluster-identifier cluster-2 \
        --backup-retention-period 14 \
        --master-user-password newpassword99 \
        --apply-immediately


Output::

    {
        "DBCluster": {
            "AllocatedStorage": 1,
            "AvailabilityZones": [
                "eu-central-1b",
                "eu-central-1c",
                "eu-central-1a"
            ],
            "BackupRetentionPeriod": 14,
            "DatabaseName": "",
            "DBClusterIdentifier": "cluster-2",
            "DBClusterParameterGroup": "default.aurora5.6",
            "DBSubnetGroup": "default-vpc-2305ca49",
            "Status": "available",
            "EarliestRestorableTime": "2020-06-03T02:07:29.637Z",
            "Endpoint": "cluster-2.cluster-############.eu-central-1.rds.amazonaws.com",
            "ReaderEndpoint": "cluster-2.cluster-ro-############.eu-central-1.rds.amazonaws.com",
            "MultiAZ": false,
            "Engine": "aurora",
            "EngineVersion": "5.6.10a",
            "LatestRestorableTime": "2020-06-04T15:11:25.748Z",
            "Port": 3306,
            "MasterUsername": "admin",
            "PreferredBackupWindow": "01:55-02:25",
            "PreferredMaintenanceWindow": "thu:21:14-thu:21:44",
            "ReadReplicaIdentifiers": [],
            "DBClusterMembers": [
                {
                    "DBInstanceIdentifier": "cluster-2-instance-1",
                    "IsClusterWriter": true,
                    "DBClusterParameterGroupStatus": "in-sync",
                    "PromotionTier": 1
                }
            ],
            "VpcSecurityGroups": [
                {
                    "VpcSecurityGroupId": "sg-20a5c047",
                    "Status": "active"
                }
            ],
            "HostedZoneId": "Z1RLNU0EXAMPLE",
            "StorageEncrypted": true,
            "KmsKeyId": "arn:aws:kms:eu-central-1:123456789012:key/d1bd7c8f-5cdb-49ca-8a62-a1b2c3d4e5f6",
            "DbClusterResourceId": "cluster-AGJ7XI77XVIS6FUXHU1EXAMPLE",
            "DBClusterArn": "arn:aws:rds:eu-central-1:123456789012:cluster:cluster-2",
            "AssociatedRoles": [],
            "IAMDatabaseAuthenticationEnabled": false,
            "ClusterCreateTime": "2020-04-03T14:44:02.764Z",
            "EngineMode": "provisioned",
            "DeletionProtection": false,
            "HttpEndpointEnabled": false,
            "CopyTagsToSnapshot": true,
            "CrossAccountClone": false,
            "DomainMemberships": []
        }
    }

For more information, see `Modifying an Amazon Aurora DB Cluster <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Modifying.html>`__ in the *Amazon Aurora User Guide*.
