# ./cloudrun-manifests

1. Create your Service Account with `.json` key and put it on `key/tf-key.json`

2. Provision Infrastructure

```
$ terraform init
$ terraform apply
```

> Most importantly, each service can only access other private services if it follows this authentication: https://cloud.google.com/run/docs/tutorials/secure-services
