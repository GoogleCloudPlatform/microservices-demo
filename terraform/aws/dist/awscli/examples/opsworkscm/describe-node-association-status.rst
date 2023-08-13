**To describe node association status**

The following ``describe-node-association-status`` command returns the status of a
request to associate a node with a Chef Automate server named ``automate-06``.::

  aws opsworks-cm describe-node-association-status --server-name "automate-06" --node-association-status-token "AflJKl+/GoKLZJBdDQEx0O65CDi57blQe9nKM8joSok0pQ9xr8DqApBN9/1O6sLdSvlfDEKkEx+eoCHvjoWHaOs="

The output for each account attribute entry returned by the command resembles the following.
*Output*::

  {
   "NodeAssociationStatus": "IN_PROGRESS"
  }

**More Information**

For more information, see `DescribeNodeAssociationStatus`_ in the *AWS OpsWorks for Chef Automate API Reference*.

.. _`DescribeNodeAssociationStatus`: http://docs.aws.amazon.com/opsworks-cm/latest/APIReference/API_DescribeNodeAssociationStatus.html

