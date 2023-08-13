**To change an IAM role's description or session duration**

The following ``update-role`` command changes the description of the IAM role ``production-role`` to ``Main production role`` and sets the maximum session duration to 12 hours. ::

  aws iam update-role --role-name production-role --description 'Main production role' --max-session-duration 43200

For more information, see `Modifying a Role`_ in the *AWS IAM User's Guide*.

.. _`Modifying a Role`: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_manage_modify.html

