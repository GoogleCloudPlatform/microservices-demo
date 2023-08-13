**To remove a role from an instance profile**

The following ``remove-role-from-instance-profile`` command removes the role named ``Test-Role`` from the instance
profile named ``ExampleInstanceProfile``::

  aws iam remove-role-from-instance-profile --instance-profile-name ExampleInstanceProfile --role-name Test-Role

For more information, see `Instance Profiles`_ in the *Using IAM* guide.

.. _`Instance Profiles`: http://docs.aws.amazon.com/IAM/latest/UserGuide/instance-profiles.html

