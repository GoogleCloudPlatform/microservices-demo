**To activate or deactivate an access key for an IAM user**

The following ``update-access-key`` command deactivates the specified access key (access key ID and secret access key)
for the IAM user named ``Bob``::

  aws iam update-access-key --access-key-id AKIAIOSFODNN7EXAMPLE --status Inactive --user-name Bob

Deactivating the key means that it cannot be used for programmatic access to AWS. However, the key is still available and can be reactivated.

For more information, see `Creating, Modifying, and Viewing User Security Credentials`_ in the *Using IAM* guide.

.. _`Creating, Modifying, and Viewing User Security Credentials`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_CreateAccessKey.html


