**To update a kubeconfig for your cluster**

This example command updates the default kubeconfig file to use your cluster as the current context.

Command::

  aws eks update-kubeconfig --name example

Output::

  Added new context arn:aws:eks:us-west-2:012345678910:cluster/example to /Users/ericn/.kube/config