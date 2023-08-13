**To get information about your studio**

The following ``get-eula`` example lists the information about an EULA. ::

    aws nimble get-eula \
        --eula-id "EULAid"

Output::

    {
        "eula": {
            "content": "https://www.mozilla.org/en-US/MPL/2.0/",
            "createdAt": "2021-04-20T16:45:23+00:00",
            "eulaId": "gJZLygd-Srq_5NNbSfiaLg",
            "name": "Mozilla-FireFox",
            "updatedAt": "2021-04-20T16:45:23+00:00"
        }
    }

For more information, see `Accept the EULA <https://docs.aws.amazon.com/nimble-studio/latest/userguide/adding-studio-users.html#adding-studio-users-step-3>`__ in the *Amazon Nimble Studio User Guide*.