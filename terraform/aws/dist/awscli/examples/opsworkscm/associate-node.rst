**To associate nodes**

The following ``associate-node`` command associates a node named ``i-44de882p`` with
a Chef Automate server named ``automate-06``, meaning that the ``automate-06`` server
manages the node, and communicates recipe commands to the node through ``chef-client`` agent software
that is installed on the node by the associate-node command. Valid node names are EC2 instance IDs.::

  aws opsworks-cm associate-node --server-name "automate-06" --node-name "i-43de882p" --engine-attributes "Name=CHEF_ORGANIZATION,Value='MyOrganization' Name=CHEF_NODE_PUBLIC_KEY,Value='Public_key_contents'"

The output returned by the command resembles the following.
*Output*::

  {
   "NodeAssociationStatusToken": "AHUY8wFe4pdXtZC5DiJa5SOLp5o14DH//rHRqHDWXxwVoNBxcEy4V7R0NOFymh7E/1HumOBPsemPQFE6dcGaiFk"
  }

**More Information**

For more information, see `Adding Nodes Automatically in AWS OpsWorks for Chef Automate`_ in the *AWS OpsWorks User Guide*.

.. _`Adding Nodes Automatically in AWS OpsWorks for Chef Automate`: http://docs.aws.amazon.com/opsworks/latest/userguide/opscm-unattend-assoc.html

