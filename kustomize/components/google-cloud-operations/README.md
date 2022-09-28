# Integrate Online Boutique with Google Cloud Operations

By default, [Google Cloud Operations](https://cloud.google.com/products/operations) instrumentation is **turned off** for Online Boutique deployments. This includes Monitoring (Stats), Tracing, Profiler, and Debugger. This means that even if you're running this app on [GKE](https://cloud.google.com/kubernetes-engine), traces (for example) will not be exported to [Google Cloud Trace](https://cloud.google.com/trace).

You can see the instrumentation status in your deployment by opening one of the `Deployment` YAML files and seeing:

```YAML
- name: DISABLE_STATS
value: "1"
- name: DISABLE_TRACING
value: "1"
- name: DISABLE_PROFILER
value: "1"
```

If you **are** running this app on GKE, and want to re-enable Google Cloud Operations instrumentation, set the value to `0` or remove those environment variables from `Deployment` YAML. This can re-enable some or all of these integrations, for some or all Online Boutique services. Note that you will accumulate Google Cloud Operations [billing](https://cloud.google.com/stackdriver/pricing) if you re-enable these fields.

<del>
- name: DISABLE_STATS
<br>
value: "0"
<br>
- name: DISABLE_TRACING
<br>
value: "0"
<br>
- name: DISABLE_PROFILER
<br>
value: "0"
<br>
</del>

You will also need to make sure that you have the associated Google APIs enabled in your Google Cloud project:
```
gcloud services enable monitoring.googleapis.com \
    cloudtrace.googleapis.com \
    clouddebugger.googleapis.com \
    cloudprofiler.googleapis.com \
    --project ${PROJECT_ID}
```

In addition to that, if you are using Workload Identity with your GKE cluster, you will need to define custom IAM roles associated to the Google Cloud Operations services, see more information [here](/docs/workload-identity.md).

## Deploy Online Boutique integrated with Google Cloud Operations via Kustomize

To automate the deployment of Online Boutique integrated with Google Cloud Operations you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:
```
kustomize edit add components/google-cloud-operations
```

This will update the `kustomize/kustomization.yaml` file which could be similar to:
```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/google-cloud-operations
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.
