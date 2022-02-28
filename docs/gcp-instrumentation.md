# Integrating Online Boutique with Google Cloud 

By default, [Google Cloud Operations](https://cloud.google.com/products/operations) instrumentation is **turned off** for Online Boutique deployments. This includes Monitoring (Stats), Tracing, Profiler, and Debugger. This means that even if you're running this app on [GKE](https://cloud.google.com/kubernetes-engine), traces (for example) will not be exported to [Google Cloud Trace](https://cloud.google.com/trace).

You can see the instrumentation status in your deployment by opening one of the Deployment YAML files and seeing:

```YAML
- name: DISABLE_STATS
value: "1"
- name: DISABLE_TRACING
value: "1"
- name: DISABLE_PROFILER
value: "1"
```

If you **are** running this app on GKE, and want to re-enable Google Cloud Operations instrumentation, remove those environment variables from deployment YAML. This can re-enable some or all of these integrations, for some or all Online Boutique services. Note that you will accumulate Google Cloud Operations [billing](https://cloud.google.com/stackdriver/pricing) if you re-enable these fields.

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
