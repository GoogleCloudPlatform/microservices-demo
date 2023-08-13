**To generate a credential report**

The following example attempts to generate a credential report for the AWS account::

  aws iam generate-credential-report

Output::

  {
      "State":  "STARTED",
	  "Description": "No report exists. Starting a new report generation task"
  }

For more information, see `Getting Credential Reports for Your AWS Account`_ in the *Using IAM* guide.

.. _`Getting Credential Reports for Your AWS Account`: http://docs.aws.amazon.com/IAM/latest/UserGuide/credential-reports.html