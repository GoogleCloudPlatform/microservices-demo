**To configure Security Hub to automatically enable new organization accounts**

The following ``update-organization-configuration`` example configures Security Hub to automatically enable new accounts in an organization. ::

    aws securityhub update-organization-configuration \
        --auto-enable

This command produces no output.

For more information, see `Automatically enabling new organization accounts <https://docs.aws.amazon.com/securityhub/latest/userguide/accounts-orgs-auto-enable.html>`__ in the *AWS Security Hub User Guide*.
