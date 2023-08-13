**To update a cluster Kubernetes version**

This example command updates a cluster named ``example`` from Kubernetes 1.12 to 1.13.

Command::

  aws eks update-cluster-version --name example --kubernetes-version 1.13

Output::

  {
      "update": {
          "id": "161a74d1-7e8c-4224-825d-b32af149f23a",
          "status": "InProgress",
          "type": "VersionUpdate",
          "params": [
              {
                  "type": "Version",
                  "value": "1.13"
              },
              {
                  "type": "PlatformVersion",
                  "value": "eks.2"
              }
          ],
          "createdAt": 1565807633.514,
          "errors": []
      }
  }
