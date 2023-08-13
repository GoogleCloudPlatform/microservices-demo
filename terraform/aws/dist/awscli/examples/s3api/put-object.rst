The following example uses the ``put-object`` command to upload an object to Amazon S3::

    aws s3api put-object --bucket text-content --key dir-1/my_images.tar.bz2 --body my_images.tar.bz2

The following example shows an upload of a video file (The video file is
specified using Windows file system syntax.)::

    aws s3api put-object --bucket text-content --key dir-1/big-video-file.mp4 --body e:\media\videos\f-sharp-3-data-services.mp4

For more information about uploading objects, see `Uploading Objects`_ in the *Amazon S3 Developer Guide*.

.. _`Uploading Objects`: http://docs.aws.amazon.com/AmazonS3/latest/dev/UploadingObjects.html

