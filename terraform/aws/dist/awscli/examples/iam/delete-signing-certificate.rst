**To delete a signing certificate for an IAM user**

The following ``delete-signing-certificate`` command deletes the specified signing certificate for the IAM user named ``Bob``::

  aws iam delete-signing-certificate --user-name Bob --certificate-id TA7SMP42TDN5Z26OBPJE7EXAMPLE

To get the ID for a signing certificate, use the ``list-signing-certificates`` command.

For more information, see `Creating and Uploading a User Signing Certificate`_ in the *Using IAM* guide.

.. _`Creating and Uploading a User Signing Certificate`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_UploadCertificate.html

