The following ``rb`` command removes a bucket.  In this example, the user's bucket is ``mybucket``.  Note that the bucket must be empty in order to remove::

    aws s3 rb s3://mybucket

Output::

    remove_bucket: mybucket

The following ``rb`` command uses the ``--force`` parameter to first remove all of the objects in the bucket and then
remove the bucket itself.  In this example, the user's bucket is ``mybucket`` and the objects in ``mybucket`` are
``test1.txt`` and ``test2.txt``::

    aws s3 rb s3://mybucket --force

Output::

    delete: s3://mybucket/test1.txt
    delete: s3://mybucket/test2.txt
    remove_bucket: mybucket

