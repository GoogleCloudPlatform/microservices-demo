**To disassociate nodes**

The following ``disassociate-node`` command disassociates a node named ``i-44de882p``, removing the node from
management by a Chef Automate server named ``automate-06``. Valid node names are EC2 instance IDs.::

  aws opsworks-cm disassociate-node --server-name "automate-06" --node-name "i-43de882p" --engine-attributes "Name=CHEF_ORGANIZATION,Value='MyOrganization' Name=CHEF_NODE_PUBLIC_KEY,Value='Public_key_contents'"

The output returned by the command resembles the following.
*Output*::

  {
   "NodeAssociationStatusToken": "AHUY8wFe4pdXtZC5DiJa5SOLp5o14DH//rHRqHDWXxwVoNBxcEy4V7R0NOFymh7E/1HumOBPsemPQFE6dcGaiFk"
  }

**More Information**

For more information, see `Delete an AWS OpsWorks for Chef Automate Server`_ in the *AWS OpsWorks User Guide*.

.. _`Delete an AWS OpsWorks for Chef Automate Server`: http://docs.aws.amazon.com/opsworks/latest/userguide/opscm-delete-server.html
