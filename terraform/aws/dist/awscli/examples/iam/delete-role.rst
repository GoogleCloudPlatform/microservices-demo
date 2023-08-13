**To delete an IAM role**

The following ``delete-role`` command removes the role named ``Test-Role``::

  aws iam delete-role --role-name Test-Role

Before you can delete a role, you must remove the role from any instance profile (``remove-role-from-instance-profile``), detach any managed policies (``detach-role-policy``) and delete any inline policies that are attached to the role (``delete-role-policy``).

For more information, see `Creating a Role`_ and `Instance Profiles`_ in the *Using IAM* guide.

.. _`Creating a Role`: http://docs.aws.amazon.com/IAM/latest/UserGuide/creating-role.html
.. _Instance Profiles: http://docs.aws.amazon.com/IAM/latest/UserGuide/instance-profiles.html


