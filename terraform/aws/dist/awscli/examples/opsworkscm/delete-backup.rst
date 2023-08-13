**To delete backups**

The following ``delete-backup`` command deletes a manual or automated backup of
a Chef Automate server, identified by the backup ID. This command is useful when
you are approaching the maximum number of backups that you can save, or you want
to minimize your Amazon S3 storage costs.::

  aws opsworks-cm delete-backup --backup-id "automate-06-2016-11-19T23:42:40.240Z"

The output shows whether the backup deletion succeeded.

**More Information**

For more information, see `Back Up and Restore an AWS OpsWorks for Chef Automate Server`_ in the *AWS OpsWorks User Guide*.

.. _`Back Up and Restore an AWS OpsWorks for Chef Automate Server`: http://docs.aws.amazon.com/opsworks/latest/userguide/opscm-backup-restore.html

