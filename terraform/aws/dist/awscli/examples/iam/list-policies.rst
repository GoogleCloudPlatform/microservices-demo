**To list managed policies that are available to your AWS account**

This example returns a collection of the first two managed policies available in the current AWS account::

  aws iam list-policies --max-items 2

Output::

  {
      "Marker": "AAIWFnoA2MQ9zN9nnTorukxr1uesDIDa4u+q1mEfaurCDZ1AuCYagYfayKYGvu75BEGk8PooPsw5uvumkuizFACZ8f4rKtN1RuBWiVDBWet2OA==",
	  "IsTruncated": true,
	  "Policies": [
	  {
		  "PolicyName": "AdministratorAccess",
		  "CreateDate": "2015-02-06T18:39:46Z",
		  "AttachmentCount": 5,
		  "IsAttachable": true,
		  "PolicyId": "ANPAIWMBCKSKIEE64ZLYK",
		  "DefaultVersionId": "v1",
		  "Path": "/",
		  "Arn": "arn:aws:iam::aws:policy/AdministratorAccess",
		  "UpdateDate": "2015-02-06T18:39:46Z"
		},
		{
		  "PolicyName": "ASamplePolicy",
          	  "CreateDate": "2015-06-17T19:23;32Z",
          	  "AttachmentCount": "0",
          	  "IsAttachable": "true",
		  "PolicyId": "Z27SI6FQMGNQ2EXAMPLE1",
          	  "DefaultVersionId": "v1",
		  "Path": "/",
		  "Arn": "arn:aws:iam::123456789012:policy/ASamplePolicy",
		  "UpdateDate": "2015-06-17T19:23:32Z"
		}
	  ]
  }

For more information, see `Overview of IAM Policies`_ in the *Using IAM* guide.

.. _`Overview of IAM Policies`: http://docs.aws.amazon.com/IAM/latest/UserGuide/policies_overview.html
