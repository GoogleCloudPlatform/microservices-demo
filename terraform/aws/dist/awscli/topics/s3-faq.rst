:title: AWS CLI S3 FAQ
:description: Frequented Asked Questions for Amazon S3 in the AWS CLI
:category: S3
:related command: s3 cp, s3 sync, s3 mv, s3 rm


S3 FAQ
======

Below are common questions regarding the use of Amazon S3 in the AWS CLI.


Q: Does the AWS CLI validate checksums?
---------------------------------------

The AWS CLI will perform checksum validation for uploading files in 
specific scenarios.

Upload
~~~~~~

The AWS CLI will calculate and auto-populate the ``Content-MD5`` header for
both standard and multipart uploads.  If the checksum that S3 calculates does
not match the ``Content-MD5`` provided, S3 will not store the object and
instead will return an error message back the AWS CLI.  The AWS CLI will retry
this error up to 5 times before giving up.  On the case that any files fail to
transfer successfully to S3, the AWS CLI will exit with a non zero RC.
See ``aws help return-codes`` for more information.

If the upload request is signed with Signature Version 4, then the AWS CLI uses the
``x-amz-content-sha256`` header as a checksum instead of ``Content-MD5``.
The AWS CLI will use Signature Version 4 for S3 in several cases:

* You're using an AWS region that only supports Signature Version 4.  This
  includes ``eu-central-1`` and ``ap-northeast-2``.
* You explicitly opt in and set ``signature_version = s3v4`` in your
  ``~/.aws/config`` file.

Note that the AWS CLI will add a ``Content-MD5`` header for both
the high level ``aws s3`` commands that perform uploads
(``aws s3 cp``, ``aws s3 sync``) as well as the low level ``s3api``
commands including ``aws s3api put-object`` and ``aws s3api upload-part``.

If you want to verify the integrity of an object during upload, see `How can I check the integrity of an object uploaded to Amazon S3? <https://aws.amazon.com/premiumsupport/knowledge-center/data-integrity-s3/>`_ in the *AWS Knowledge Center*.
