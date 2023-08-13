**To delete imported key material from a KMS key**

The following ``delete-imported-key-material`` example deletes key material that had been imported into a KMS key. ::

    aws kms delete-imported-key-material \
       --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

This command produces no output. To verify that the key material is deleted, use the ``describe-key`` command to look for a key state of ``PendingImport`` or ``PendingDeletion``.

For more information, see `Deleting imported key material<https://docs.aws.amazon.com/kms/latest/developerguide/importing-keys-delete-key-material.html>`__ in the *AWS Key Management Service Developer Guide*.