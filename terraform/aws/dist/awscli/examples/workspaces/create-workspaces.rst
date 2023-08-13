**Example 1: To create an AlwaysOn WorkSpace**

The following ``create-workspaces`` example creates an AlwaysOn WorkSpace for the specified user, using the specified directory and bundle. ::

    aws workspaces create-workspaces \
        --workspaces DirectoryId=d-926722edaf,UserName=Mateo,BundleId=wsb-0zsvgp8fc

Output::

    {
        "FailedRequests": [],
        "PendingRequests": [
            {
                "WorkspaceId": "ws-kcqms853t",
                "DirectoryId": "d-926722edaf",
                "UserName": "Mateo",
                "State": "PENDING",
                "BundleId": "wsb-0zsvgp8fc"
            }
        ]
    }

**Example 2: To create an AutoStop WorkSpace**

The following ``create-workspaces`` example creates an AutoStop WorkSpace for the specified user, using the specified directory and bundle. ::

    aws workspaces create-workspaces \
        --workspaces DirectoryId=d-926722edaf,UserName=Mary,BundleId=wsb-0zsvgp8fc,WorkspaceProperties={RunningMode=AUTO_STOP}

Output::

    {
        "FailedRequests": [],
        "PendingRequests": [
            {
                "WorkspaceId": "ws-dk1xzr417",
                "DirectoryId": "d-926722edaf",
                "UserName": "Mary",
                "State": "PENDING",
                "BundleId": "wsb-0zsvgp8fc"
            }
        ]
    }

For more information, see `Launch a virtual desktop <https://docs.aws.amazon.com/workspaces/latest/adminguide/launch-workspaces-tutorials.html>`__ in the *Amazon WorkSpaces Administration Guide*.
