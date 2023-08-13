**To get information about a group**

This example gets information about a group named MyGroup.

Command::

  aws cognito-idp get-group --user-pool-id us-west-2_aaaaaaaaa --group-name MyGroup

Output::

  {
    "Group": {
        "GroupName": "MyGroup",
        "UserPoolId": "us-west-2_aaaaaaaaa",
        "Description": "A sample group.",
        "LastModifiedDate": 1548270073.795,
        "CreationDate": 1548270073.795
    }
  }