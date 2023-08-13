**To determine whether a KMS key is automatically rotated.**

The following ``get-key-rotation-status`` example determines whether a KMS key is automatically rotated. You can use this command on customer managed KMS keys and AWS managed KMS keys. However, all AWS managed KMS keys are automatically rotated every year. ::

    aws kms get-key-rotation-status \
        --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

Output::

    {
        "KeyRotationEnabled": true
    }

For more information, see `Rotating keys <https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html>`__ in the *AWS Key Management Service Developer Guide*.