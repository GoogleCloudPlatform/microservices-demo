**To restore a server**

The following ``restore-server`` command performs an in-place restoration of a 
Chef Automate server named ``automate-06`` in your default region from a backup
with an ID of ``automate-06-2016-11-22T16:13:27.998Z``. Restoring a server restores
connections to the nodes that the Chef Automate server was managing at the time 
that the specified backup was performed.

  aws opsworks-cm restore-server --backup-id "automate-06-2016-11-22T16:13:27.998Z" --server-name "automate-06"

The output is the command ID only.
*Output*::

  (None)

**More Information**

For more information, see `Restore a Failed AWS OpsWorks for Chef Automate Server`_ in the *AWS OpsWorks User Guide*.

.. _`Restore a Failed AWS OpsWorks for Chef Automate Server`: http://docs.aws.amazon.com/opsworks/latest/userguide/opscm-chef-restore.html
