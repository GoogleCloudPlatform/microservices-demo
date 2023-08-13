**To describe a placement for a project**

The following ``describe-placement`` example describes a placement for the specified project. ::

    aws iot1click-projects describe-placement \
        --project-name AnytownDumpsters \
        --placement-name customer217

Output::

   {
       "placement": {
           "projectName": "AnytownDumpsters",
           "placementName": "customer217",
           "attributes": {
               "phone": "123-555-0110",
               "location": "123 Any Street Anytown, USA 10001"
           },
           "createdDate": 1563488454,
           "updatedDate": 1563488454
       }
   }

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
