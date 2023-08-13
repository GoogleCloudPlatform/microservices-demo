The following ``rm`` command deletes a single s3 object::

    aws s3 rm s3://mybucket/test2.txt

Output::

    delete: s3://mybucket/test2.txt

The following ``rm`` command recursively deletes all objects under a specified bucket and prefix when passed with the
parameter ``--recursive``.  In this example, the bucket ``mybucket`` contains the objects ``test1.txt`` and
``test2.txt``::

    aws s3 rm s3://mybucket --recursive

Output::

    delete: s3://mybucket/test1.txt
    delete: s3://mybucket/test2.txt

The following ``rm`` command recursively deletes all objects under a specified bucket and prefix when passed with the
parameter ``--recursive`` while excluding some objects by using an ``--exclude`` parameter.  In this example, the bucket
``mybucket`` has the objects ``test1.txt`` and ``test2.jpg``::

    aws s3 rm s3://mybucket/ --recursive --exclude "*.jpg"

Output::

    delete: s3://mybucket/test1.txt

The following ``rm`` command recursively deletes all objects under a specified bucket and prefix when passed with the
parameter ``--recursive`` while excluding all objects under a particular prefix by using an ``--exclude`` parameter.  In
this example, the bucket ``mybucket`` has the objects ``test1.txt`` and ``another/test.txt``::

    aws s3 rm s3://mybucket/ --recursive --exclude "another/*"

Output::

    delete: s3://mybucket/test1.txt


**Deleting an object from an S3 access point**

The following ``rm`` command deletes a single object (``mykey``) from the access point (``myaccesspoint``)::

    aws s3 rm s3://arn:aws:s3:us-west-2:123456789012:accesspoint/myaccesspoint/mykey

Output::

    delete: s3://arn:aws:s3:us-west-2:123456789012:accesspoint/myaccesspoint/mykey
