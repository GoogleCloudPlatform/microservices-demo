**To pause running until the specified instance profile exists**

The following ``wait instance-profile-exists`` command pauses and continues only after it can confirm that the specified instance profile exists. There is no output. ::

  aws iam wait instance-profile-exists --instance-profile-name WebServer
