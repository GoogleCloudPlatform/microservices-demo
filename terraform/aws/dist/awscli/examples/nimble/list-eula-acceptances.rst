**To list the available widgets**

The following ``list-eula-acceptances`` example lists the accepted EULAs in your AWS account. ::

    aws nimble list-eula-acceptances \
        --studio-id "StudioID"

Output::

    {
        "eulaAcceptances": [
            {
                "acceptedAt": "2022-01-28T17:44:35+00:00",
                "acceptedBy": "92677b4b19-e9fd012a-94ad-4f16-9866-c69a63ab6486",
                "accepteeId": "us-west-2:stid-nyoqq12fteqy1x48",
                "eulaAcceptanceId": "V0JlpZQaSx6yHcUuX0qfQw",
                "eulaId": "Rl-J0fM5Sl2hyIiwWIV6hw"
            },
            {
                "acceptedAt": "2022-01-28T17:44:35+00:00",
                "acceptedBy": "92677b4b19-e9fd012a-94ad-4f16-9866-c69a63ab6486",
                "accepteeId": "us-west-2:stid-nyoqq12fteqy1x48",
                "eulaAcceptanceId": "YY_uDFW-SVibc627qbug0Q",
                "eulaId": "RvoNmVXiSrS4LhLTb6ybkw"
            },
            {
                "acceptedAt": "2022-01-28T17:44:35+00:00",
                "acceptedBy": "92677b4b19-e9fd012a-94ad-4f16-9866-c69a63ab6486",
                "accepteeId": "us-west-2:stid-nyoqq12fteqy1x48",
                "eulaAcceptanceId": "ovO87PnhQ4-MpttiL5uN6Q",
                "eulaId": "a-D9Wc0VQCKUfxAinCDxaw"
            },
            {
                "acceptedAt": "2022-01-28T17:44:35+00:00",
                "acceptedBy": "92677b4b19-e9fd012a-94ad-4f16-9866-c69a63ab6486",
                "accepteeId": "us-west-2:stid-nyoqq12fteqy1x48",
                "eulaAcceptanceId": "5YeXje4yROamuTESGvqIAQ",
                "eulaId": "gJZLygd-Srq_5NNbSfiaLg"
            },
            {
                "acceptedAt": "2022-01-28T17:44:35+00:00",
                "acceptedBy": "92677b4b19-e9fd012a-94ad-4f16-9866-c69a63ab6486",
                "accepteeId": "us-west-2:stid-nyoqq12fteqy1x48",
                "eulaAcceptanceId": "W1sIn8PtScqeJEn8sxxhgw",
                "eulaId": "ggK2eIw6RQyt8PIeeOlD3g"
            },
            {
                "acceptedAt": "2022-01-28T17:44:35+00:00",
                "acceptedBy": "92677b4b19-e9fd012a-94ad-4f16-9866-c69a63ab6486",
                "accepteeId": "us-west-2:stid-nyoqq12fteqy1x48",
                "eulaAcceptanceId": "Zq9KNEQPRMWJ7FolSoQgUA",
                "eulaId": "wtp85BcSTa2NZeNRnMKdjw"
            }
        ]
    }

For more information, see `Accept the EULA <https://docs.aws.amazon.com/nimble-studio/latest/userguide/adding-studio-users.html#adding-studio-users-step-3>`__ in the *Amazon Nimble Studio User Guide*.