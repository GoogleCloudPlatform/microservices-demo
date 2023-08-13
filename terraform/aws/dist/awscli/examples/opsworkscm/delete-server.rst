**To delete servers**

The following ``delete-server`` command deletes a Chef Automate server, identified
by the server's name. After the server is deleted, it is no longer returned by
``DescribeServer`` requests.::

  aws opsworks-cm delete-server --server-name "automate-06"

The output shows whether the server deletion succeeded.

**More Information**

For more information, see `Delete an AWS OpsWorks for Chef Automate Server`_ in the *AWS OpsWorks User Guide*.

.. _`Delete an AWS OpsWorks for Chef Automate Server`: http://docs.aws.amazon.com/opsworks/latest/userguide/opscm-delete-server.html

