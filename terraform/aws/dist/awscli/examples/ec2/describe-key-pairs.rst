**To display a key pair**

This example displays the fingerprint for the key pair named ``MyKeyPair``.

Command::

  aws ec2 describe-key-pairs --key-name MyKeyPair

Output::

  {
      "KeyPairs": [
          {
              "KeyName": "MyKeyPair",
              "KeyFingerprint": "1f:51:ae:28:bf:89:e9:d8:1f:25:5d:37:2d:7d:b8:ca:9f:f5:f1:6f"
          }
      ]
  }

For more information, see `Using Key Pairs`_ in the *AWS Command Line Interface User Guide*.

.. _`Using Key Pairs`: http://docs.aws.amazon.com/cli/latest/userguide/cli-ec2-keypairs.html

