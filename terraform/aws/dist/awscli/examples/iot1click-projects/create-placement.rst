**To create an AWS IoT 1-Click placement for a project**

The following ``create-placement`` example  create an AWS IoT 1-Click placement for the specified project. ::

    aws iot1click-projects create-placement \
        --project-name AnytownDumpsters \
        --placement-name customer217 \
        --attributes "{"location": "123 Any Street Anytown, USA 10001", "phone": "123-456-7890"}"

This command produces no output.

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
