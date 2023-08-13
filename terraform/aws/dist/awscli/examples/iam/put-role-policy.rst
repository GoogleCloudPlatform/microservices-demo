**To attach a permissions policy to an IAM role**

The following ``put-role-policy`` command adds a permissions policy to the role named ``Test-Role``::

  aws iam put-role-policy --role-name Test-Role --policy-name ExamplePolicy --policy-document file://AdminPolicy.json

The policy is defined as a JSON document in the *AdminPolicy.json* file. (The file name and extension do not have significance.)

To attach a trust policy to a role, use the ``update-assume-role-policy`` command.

For more information, see `Creating a Role`_ in the *Using IAM* guide.

.. _`Creating a Role`: http://docs.aws.amazon.com/IAM/latest/UserGuide/creating-role.html

