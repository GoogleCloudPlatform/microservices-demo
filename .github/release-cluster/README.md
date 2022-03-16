# onlineboutique.dev manifests

This directory contains extra deploy manifests for configuring Online Boutique solution on GKE for onlineboutique.dev.

_Note: before moving forward, the OnlineBoutique apps should already be deployed [on the online-boutique-release GKE cluster](../../hack#10-deploy-releasekubernetes-manifestsyaml-to-our-online-boutique-release-gke-cluster)._

## Public static IP address

Create the static public IP address:
```
STATIC_IP_NAME=online-boutique-ip # name hard-coded in: frontend-ingress.yaml
gcloud compute addresses create $STATIC_IP_NAME --global
```

When ready to do so, you could grab this public IP address and update your DNS:
```
gcloud compute addresses describe $STATIC_IP_NAME \
    --global \
    --format "value(address)"
```

## Cloud Armor

Set up Cloud Armor:
```
SECURITY_POLICY_NAME=online-boutique-security-policy # Name hard-coded in: backendconfig.yaml
gcloud compute security-policies create $SECURITY_POLICY_NAME \
    --description "Block various attacks"
gcloud compute security-policies rules create 1000 \
    --security-policy $SECURITY_POLICY_NAME \
    --expression "evaluatePreconfiguredExpr('xss-stable')" \
    --action "deny-403" \
    --description "XSS attack filtering"
gcloud compute security-policies rules create 12345 \
    --security-policy $SECURITY_POLICY_NAME \
    --expression "evaluatePreconfiguredExpr('cve-canary')" \
    --action "deny-403" \
    --description "CVE-2021-44228 and CVE-2021-45046"
gcloud compute security-policies update $SECURITY_POLICY_NAME \
    --enable-layer7-ddos-defense
gcloud compute security-policies update $SECURITY_POLICY_NAME \
    --log-level=VERBOSE
```

## SSL Policy

Set up an SSL policy in order to later set up a redirect from HTTP to HTTPs:
```
SSL_POLICY_NAME=online-boutique-ssl-policy # Name hard-coded in: frontendconfig.yaml
gcloud compute ssl-policies create $SSL_POLICY_NAME \
    --profile COMPATIBLE  \
    --min-tls-version 1.0
```

## Deploy Kubernetes manifests

Deploy the Kubernetes manifests in this current folder:
```
kubectl apply -f .
```

Wait for the `ManagedCertificate` to be provisioned. This usually takes about 30 minutes.
```
kubectl get managedcertificates
```

Remove the default `LoadBalancer` `Service` not used at this point:
```
kubectl delete service frontend-external
```

Remove the `loadgenerator` `Deployment` not used at this point:
```
kubectl delete deployment loadgenerator
```