**To get a credential report**

This example opens the returned report and outputs it to the pipeline as an array of text lines::

  aws iam get-credential-report

Output::

  {
      "GeneratedTime":  "2015-06-17T19:11:50Z",
	  "ReportFormat": "text/csv"
  }

For more information, see `Getting Credential Reports for Your AWS Account`_ in the *Using IAM* guide.

.. _`Getting Credential Reports for Your AWS Account`: http://docs.aws.amazon.com/IAM/latest/UserGuide/credential-reports.html