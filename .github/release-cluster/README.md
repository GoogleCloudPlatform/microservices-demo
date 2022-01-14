# onlineboutique.dev manifests

This directory contains extra deploy manifests for configuring a domain name/static IP to point to an Online Boutique deployment running in GKE.

Create the static Public IP address:
```
gcloud compute addresses create online-boutique-ip --global
```

When ready to do so, you could grab this Public IP address and update your DNS:
```
gcloud compute addresses describe $staticIpName \
    --global \
    --format "value(address)"
```

Setup Cloud Armor:
```
securityPolicyName=online-boutique-security-policy # Name hard-coded in: backendconfig.yaml
gcloud compute security-policies create $securityPolicyName \
    --description "Block XSS attacks"
gcloud compute security-policies rules create 1000 \
    --security-policy $securityPolicyName \
    --expression "evaluatePreconfiguredExpr('xss-stable')" \
    --action "deny-403" \
    --description "XSS attack filtering"
gcloud compute security-policies rules create 12345 \
    --security-policy $securityPolicyName \
    --expression "evaluatePreconfiguredExpr('cve-canary')" \
    --action "deny-403" \
    --description "CVE-2021-44228 and CVE-2021-45046"
gcloud compute security-policies update $securityPolicyName \
    --enable-layer7-ddos-defense
gcloud compute security-policies update $securityPolicyName \
    --log-level=VERBOSE
```

Setup an SSL policy in order to setup later a redirect from http to https:
```
sslPolicyName=online-boutique-ssl-policy # Name hard-coded in: frontendconfig.yaml
gcloud compute ssl-policies create $sslPolicyName \
    --profile COMPATIBLE  \
    --min-tls-version 1.0
```

Deploy the Kubernetes manifests:
```
kubectl apply -f .
```

Remove the default `LoadBalancer` `Service` not used anymore:
```
kubectl delete service frontend-external
```