**To get a cluster authentication token**

This example command gets an authentication token for a cluster named ``example``.

Command::

  aws eks get-token --cluster-name example

Output::

  {
    "kind": "ExecCredential",
    "apiVersion": "client.authentication.k8s.io/v1beta1",
    "spec": {},
    "status": {
      "expirationTimestamp": "2019-08-14T18:44:27Z",
      "token": "k8s-aws-v1EXAMPLE_TOKEN_DATA_STRING..."
    }
  }
