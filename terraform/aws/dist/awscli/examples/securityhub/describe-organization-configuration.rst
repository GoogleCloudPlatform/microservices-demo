**To view information about an integration with AWS Organizations**

The following ``describe-organization-configuration`` example returns information about the integration with Organizations. ::

    aws securityhub describe-organization-configuration

Output::

    {
        "autoEnable": true,
        "memberAccountLimitReached": false
    }

For more information, see `Managing accounts <https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-accounts.html>`__ in the *AWS Security Hub User Guide*.
