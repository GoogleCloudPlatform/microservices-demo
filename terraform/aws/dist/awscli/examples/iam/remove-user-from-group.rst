**To remove a user from an IAM group**

The following ``remove-user-from-group`` command removes the user named ``Bob`` from the IAM group named ``Admins``::

  aws iam remove-user-from-group --user-name Bob --group-name Admins

For more information, see `Adding Users to and Removing Users from a Group`_ in the *Using IAM* guide.

.. _`Adding Users to and Removing Users from a Group`: http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_AddOrRemoveUsersFromGroup.html

