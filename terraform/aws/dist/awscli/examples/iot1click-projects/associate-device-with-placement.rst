**To associate an AWS IoT 1-Click device with an existing placement**

The following ``associate-device-with-placement`` example associates the specified AWS IoT 1-Click device with an existing placement. ::

    aws iot1click-projects associate-device-with-placement \
        --project-name AnytownDumpsters \
        --placement-name customer217 \
        --device-template-name empty-dumpster-request \
        --device-id G030PM0123456789

This command produces no output.

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
