**To list the available widgets**

The following ``list-eulas`` example lists the EULAs in your AWS account. ::

    aws nimble list-eulas

Output::

    {
        "eulas": [
            {
                "content": "https://www.mozilla.org/en-US/MPL/2.0/",
                "createdAt": "2021-04-20T16:45:23+00:00",
                "eulaId": "gJZLygd-Srq_5NNbSfiaLg",
                "name": "Mozilla-FireFox",
                "updatedAt": "2021-04-20T16:45:23+00:00"
            },
            {
                "content": "https://www.awsthinkbox.com/end-user-license-agreement",
                "createdAt": "2021-04-20T16:45:24+00:00",
                "eulaId": "RvoNmVXiSrS4LhLTb6ybkw",
                "name": "Thinkbox-Deadline",
                "updatedAt": "2021-04-20T16:45:24+00:00"
            },
            {
                "content": "https://www.videolan.org/legal.html",
                "createdAt": "2021-04-20T16:45:24+00:00",
                "eulaId": "Rl-J0fM5Sl2hyIiwWIV6hw",
                "name": "Videolan-VLC",
                "updatedAt": "2021-04-20T16:45:24+00:00"
            },
            {
                "content": "https://code.visualstudio.com/license",
                "createdAt": "2021-04-20T16:45:23+00:00",
                "eulaId": "ggK2eIw6RQyt8PIeeOlD3g",
                "name": "Microsoft-VSCode",
                "updatedAt": "2021-04-20T16:45:23+00:00"
            },
            {
                "content": "https://darbyjohnston.github.io/DJV/legal.html#License",
                "createdAt": "2021-04-20T16:45:23+00:00",
                "eulaId": "wtp85BcSTa2NZeNRnMKdjw",
                "name": "DJV-DJV",
                "updatedAt": "2021-04-20T16:45:23+00:00"
            },
            {
                "content": "https://www.sidefx.com/legal/license-agreement/",
                "createdAt": "2021-04-20T16:45:24+00:00",
                "eulaId": "uu2VDLo-QJeIGWWLBae_UA",
                "name": "SideFX-Houdini",
                "updatedAt": "2021-04-20T16:45:24+00:00"
            },
            {
                "content": "https://www.chaosgroup.com/eula",
                "createdAt": "2021-04-20T16:45:23+00:00",
                "eulaId": "L0HS4P3CRYKVXc2J2LO7Vw",
                "name": "ChaosGroup-Vray",
                "updatedAt": "2021-04-20T16:45:23+00:00"
            },
            {
                "content": "https://www.foundry.com/eula",
                "createdAt": "2021-04-20T16:45:23+00:00",
                "eulaId": "SAuhfHmmSAeUuq3wsMiMlw",
                "name": "Foundry-Nuke",
                "updatedAt": "2021-04-20T16:45:23+00:00"
            },
            {
                "content": "https://download.blender.org/release/GPL3-license.txt",
                "createdAt": "2021-04-20T16:45:23+00:00",
                "eulaId": "a-D9Wc0VQCKUfxAinCDxaw",
                "name": "BlenderFoundation-Blender",
                "updatedAt": "2021-04-20T16:45:23+00:00"
            }
        ]
    }

For more information, see `Accept the EULA <https://docs.aws.amazon.com/nimble-studio/latest/userguide/adding-studio-users.html#adding-studio-users-step-3>`__ in the *Amazon Nimble Studio User Guide*.