**To return the provisioning parameters for a stack**

The following ``describe-stack-provisioning-parameters`` example returns the provisioning parameters for a specified stack. Provisioning parameters include settings such as the agent installation location and public key that OpsWorks uses to manage the agent on instances in a stack. ::

    aws opsworks describe-stack-provisioning-parameters \
        --stack-id 62744d97-6faf-4ecb-969b-a086fEXAMPLE

Output::

    {
        "AgentInstallerUrl": "https://opsworks-instance-agent-us-west-2.s3.amazonaws.com/ID_number/opsworks-agent-installer.tgz",
        "Parameters": {
            "agent_installer_base_url": "https://opsworks-instance-agent-us-west-2.s3.amazonaws.com",
            "agent_installer_tgz": "opsworks-agent-installer.tgz",
            "assets_download_bucket": "opsworks-instance-assets-us-west-2.s3.amazonaws.com",
            "charlie_public_key": "-----BEGIN PUBLIC KEY-----PUBLIC_KEY_EXAMPLE\n-----END PUBLIC KEY-----",
            "instance_service_endpoint": "opsworks-instance-service.us-west-2.amazonaws.com",
            "instance_service_port": "443",
            "instance_service_region": "us-west-2",
            "instance_service_ssl_verify_peer": "true",
            "instance_service_use_ssl": "true",
            "ops_works_endpoint": "opsworks.us-west-2.amazonaws.com",
            "ops_works_port": "443",
            "ops_works_region": "us-west-2",
            "ops_works_ssl_verify_peer": "true",
            "ops_works_use_ssl": "true",
            "verbose": "false",
            "wait_between_runs": "30"
        }
    }

For more information, see `Run Stack Commands <https://docs.aws.amazon.com/opsworks/latest/userguide/workingstacks-commands.html>`__ in the *AWS OpsWorks User Guide*.
