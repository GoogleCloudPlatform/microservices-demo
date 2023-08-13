**To pause running until the specified role exists**

The following ``wait policy-exists`` command pauses and continues only after it can confirm that the specified policy exists. There is no output. ::

  aws iam wait policy-exists --policy-arn arn:aws:iam::123456789012:policy/MyPolicy
