**To describe an update for a cluster**

This example command describes an update for a cluster named ``example`` in your default region.

Command::

  aws eks describe-update --name example \
  --update-id 10bddb13-a71b-425a-b0a6-71cd03e59161

Output::

  {
      "update": {
          "id": "10bddb13-a71b-425a-b0a6-71cd03e59161",
          "status": "Successful",
          "type": "EndpointAccessUpdate",
          "params": [
              {
                  "type": "EndpointPublicAccess",
                  "value": "true"
              },
              {
                  "type": "EndpointPrivateAccess",
                  "value": "false"
              }
          ],
          "createdAt": 1565806691.149,
          "errors": []
      }
  }
