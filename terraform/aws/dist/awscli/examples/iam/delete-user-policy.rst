**To remove a policy from an IAM user**

The following ``delete-user-policy`` command removes the specified policy from the IAM user named ``Bob``::

  aws iam delete-user-policy --user-name Bob --policy-name ExamplePolicy

To get a list of policies for an IAM user, use the ``list-user-policies`` command.

For more information, see `Adding a New User to Your AWS Account`_ in the *Using IAM* guide.

.. _`Adding a New User to Your AWS Account`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_SettingUpUser.html





