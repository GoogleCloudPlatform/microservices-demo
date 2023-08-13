The following ``mv`` command moves a single file to a specified bucket and key::

    aws s3 mv test.txt s3://mybucket/test2.txt

Output::

    move: test.txt to s3://mybucket/test2.txt

The following ``mv`` command moves a single s3 object to a specified bucket and key::

    aws s3 mv s3://mybucket/test.txt s3://mybucket/test2.txt

Output::

    move: s3://mybucket/test.txt to s3://mybucket/test2.txt

The following ``mv`` command moves a single object to a specified file locally::

    aws s3 mv s3://mybucket/test.txt test2.txt

Output::

    move: s3://mybucket/test.txt to test2.txt

The following ``mv`` command moves a single object to a specified bucket while retaining its original name::

    aws s3 mv s3://mybucket/test.txt s3://mybucket2/

Output::

    move: s3://mybucket/test.txt to s3://mybucket2/test.txt

When passed with the parameter ``--recursive``, the following ``mv`` command recursively moves all objects under a
specified prefix and bucket to a specified directory.  In this example, the bucket ``mybucket`` has the objects
``test1.txt`` and ``test2.txt``::

    aws s3 mv s3://mybucket . --recursive

Output::

    move: s3://mybucket/test1.txt to test1.txt
    move: s3://mybucket/test2.txt to test2.txt

When passed with the parameter ``--recursive``, the following ``mv`` command recursively moves all files under a
specified directory to a specified bucket and prefix while excluding some files by using an ``--exclude`` parameter. In
this example, the directory ``myDir`` has the files ``test1.txt`` and ``test2.jpg``::

    aws s3 mv myDir s3://mybucket/ --recursive --exclude "*.jpg"

Output::

    move: myDir/test1.txt to s3://mybucket2/test1.txt

When passed with the parameter ``--recursive``, the following ``mv`` command recursively moves all objects under a
specified bucket to another bucket while excluding some objects by using an ``--exclude`` parameter.  In this example,
the bucket ``mybucket`` has the objects ``test1.txt`` and ``another/test1.txt``::

    aws s3 mv s3://mybucket/ s3://mybucket2/ --recursive --exclude "mybucket/another/*"

Output::

    move: s3://mybucket/test1.txt to s3://mybucket2/test1.txt

The following ``mv`` command moves a single object to a specified bucket and key while setting the ACL to
``public-read-write``::

    aws s3 mv s3://mybucket/test.txt s3://mybucket/test2.txt --acl public-read-write

Output::

    move: s3://mybucket/test.txt to s3://mybucket/test2.txt

The following ``mv`` command illustrates the use of the ``--grants`` option to grant read access to all users and full
control to a specific user identified by their email address::

  aws s3 mv file.txt s3://mybucket/ --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers full=emailaddress=user@example.com

Output::

    move: file.txt to s3://mybucket/file.txt


**Moving a file to an S3 access point**

The following ``mv`` command moves a single file (``mydoc.txt``) to the access point (``myaccesspoint``) at the key (``mykey``)::

    aws s3 mv mydoc.txt s3://arn:aws:s3:us-west-2:123456789012:accesspoint/myaccesspoint/mykey

Output::

    move: mydoc.txt to s3://arn:aws:s3:us-west-2:123456789012:accesspoint/myaccesspoint/mykey

