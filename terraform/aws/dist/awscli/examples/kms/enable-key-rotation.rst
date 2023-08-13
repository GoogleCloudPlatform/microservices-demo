**To enable automatic rotation of a KMS key**

The following ``enable-key-rotation`` example enables automatic rotation of a customer managed KMS key. The KMS key will be rotated one year (approximate 365 days) from the date that this command completes and every year thereafter. ::

    aws kms enable-key-rotation \
        --key-id arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab

This command produces no output. To verify that the KMS key is enabled, use the ``get-key-rotation-status`` command.

For more information, see `Rotating keys <https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html>`__ in the *AWS Key Management Service Developer Guide*.