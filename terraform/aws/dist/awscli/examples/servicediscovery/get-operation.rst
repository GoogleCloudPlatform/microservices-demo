**To get the result of an operation**

The following ``get-operation`` example gets the result of an operation. ::

    aws servicediscovery get-operation \
        --operation-id gv4g5meo7ndmeh4fqskygvk23d2fijwa-k9302yzd

Output::

    {
        "Operation": {
            "Id": "gv4g5meo7ndmeh4fqskygvk23d2fijwa-k9302yzd",
            "Type": "CREATE_NAMESPACE",
            "Status": "SUCCESS",
            "CreateDate": 1587055860.121,
            "UpdateDate": 1587055900.469,
            "Targets": {
                "NAMESPACE": "ns-ylexjili4cdxy3xm"
            }
        }
    }

