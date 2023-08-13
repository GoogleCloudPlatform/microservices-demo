**To set the global endpoint token version**

The following ``set-security-token-service-preferences`` example configures Amazon STS to use version 2 tokens when you authenticate against the global endpoint. ::

    aws iam set-security-token-service-preferences \
        --global-endpoint-token-version v2Token

This command produces no output.
