**To disassociate a device from a placement**

The following ``disassociate-device-from-placement`` example disassociates the specified device from a placement. ::

    aws iot1click-projects disassociate-device-from-placement \
        --project-name AnytownDumpsters \
        --placement-name customer217 \
        --device-template-name empty-dumpster-request

This command produces no output.

For more information, see `Using AWS IoT 1-Click with the AWS CLI <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/1click-cli.html>`__ in the *AWS IoT 1-Click Developer Guide*.
