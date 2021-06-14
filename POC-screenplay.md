# Screenplay for POC

### Preliminaries
We assume that the [analysis tool](https://github.com/shift-left-netconfig/cluster-topology-analyzer) and
the [synthesis tool](https://github.com/shift-left-netconfig/netpol-synthesizer) are already installed
under the demo's base directory.

### Deploy Google's microservices demo (Hipster shop)

1. Clone a copy of the repo from https://github.com/shift-left-netconfig/microservices-demo
1. `cd microservices-demo`
1. Change context to `net-demo` namespace: `kubectl config set-context --current --namespace=net-demo`
1. `kubectl apply -f release/kubernetes-manifests.yaml`
1. Make sure all pods are running
1. Get the external IP of the frontend service by running `kubectl get svc frontend-external`
1. Copy-paste the external IP into a browser, to make sure the application is running

### Expose a security issue with the application
Frontend can actually connect to payment-service directly.
1. Run `kubectl exec frontend-b4df774c5-gpxlt -- wget paymentservice:50051` (replace pod-name with the actual name)

The output looks like
```
Connecting to paymentservice:50051 (172.21.109.255:50051)
wget: error getting response: Invalid argument
command terminated with exit code 1
```
So frontend was able to connect to the payment service, it just didn't use the correct arguments.

### Analyze the repo and synthesize relevant network policies

1. Run analysis: `../gitsecure-net-top/bin/net-top -dirpath . -commitid bfa5ba496e1ad30cba4545ab93ffa7082bd17eb9 -giturl https://github.com/shift-left-netconfig/microservices-demo -gitbranch matser -outputfile microservices-demo.json` 
2. Run synthesis: `../netpol-synthesizer/venv/Scripts/python ../netpol-synthesizer/src/netpol_synth.py microservices-demo.json -o release/microservices-netpols.yaml`

### Apply network policies and verify security issue is fixed

1. `kubectl apply -f release/microservices-netpols.yaml`
1. Run again `kubectl exec frontend-b4df774c5-gpxlt -- wget paymentservice:50051` (replace pod-name with the actual name)

The output should look like
```
Connecting to paymentservice (172.21.109.255:80)
wget: can't connect to remote host (172.21.109.255): Operation timed out
command terminated with exit code 1
```
This shows that the frontend can no longer connect to the payment-service.

### Add baseline requirements in the synthesis process

We would like to enforce that only deployments with a given label, say `payment_access: yes`,
will be allowed to access the payment service.
We will rerun the synthesis tool and provide it with a baseline-rules file:
```
../netpol-synthesizer/venv/Scripts/python ../netpol-synthesizer/src/netpol_synth.py microservices-demo.json -o release/microservices-netpols.yaml -b ../netpol-synthesizer/baseline-rules/examples/restrict_access_to_payment.yaml
```

Since `checkoutservice` currently does not have the required label, the synthesis tool reports a conflict (currently as a warning), and the synthesized network policies should deny access. As a result, if the policies are deployed, the application breaks.

After adding the right label to the deployment, synthesis should go smooth, and the application should not break.

### Cleaning
* Clean deployments and services: `kubectl delete -f release/kubernetes-manifests.yaml`
* Clean network policies: `kubectl delete -f release/microservices-netpols.yaml`
