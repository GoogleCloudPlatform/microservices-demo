**To attach a policy to an IAM user**

The following ``put-user-policy`` command attaches a policy to the IAM user named ``Bob``::

  aws iam put-user-policy --user-name Bob --policy-name ExamplePolicy --policy-document file://AdminPolicy.json

The policy is defined as a JSON document in the *AdminPolicy.json* file. (The file name and extension do not have significance.)

For more information, see `Adding a New User to Your AWS Account`_ in the *Using IAM* guide.

.. _`Adding a New User to Your AWS Account`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_SettingUpUser.html





