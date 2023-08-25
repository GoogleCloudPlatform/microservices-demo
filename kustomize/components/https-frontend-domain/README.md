# HTTPS domain for Online Boutique's frontend

This Kustomize component allows you to configure your Online Boutique frontend deployment to accept HTTPS (TLS) traffic from a domain that you own.

For this Kustomize component, you will need to:

* use Google Kubernetes Engine (GKE)
* own a domain name and have access to its DNS records

## Set up static IP address

Before you deploy this Kustomize component, you will need to create a static IP address on Google Cloud and point your domain's DNS to that IP address.

1. Create a static IP address:

```bash
gcloud compute addresses create my-static-ip-address --global \
    --project MY_PROJECT_ID
```

* Replace `MY_PROJECT_ID` with your Google Cloud project ID.
* If you use a name different from `my-static-ip-address` in the command above, set the value of `kubernetes.io/ingress.global-static-ip-name` inside `frontend-ingress.yaml` to the name of the static IP address.

2. Obtain the IP address.

```bash
gcloud compute addresses list --project MY_PROJECT_ID
```

* Replace `MY_PROJECT_ID` with your Google Cloud project ID.

3. Configure your DNS records for your domains to point to the static IP address.
* In your DNS, you will need to create an A record for each (sub)domain that you will use.
* Wait until your configuration propogates.
* To check if your DNS change works, you can use `nslookup example.com`.

4. Update the list of `domains` inside `frontend-managed-certificate.yaml`.

## Deploy this Kustomize component

From the `kustomize/` folder at the root level of this repository, execute this command:

```bash
kustomize edit add component components/https-frontend-domain
```

This will update the `kustomize/kustomization.yaml` file which could look similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/https-frontend-domain
```

To render the manifests (without deploying them), run:
```bash
kubectl kustomize .
```

To deploy the manifests, run:
```bash
kubectl apply -k .
```

## Delete unused `frontend-external` Service

The default deployment of Online Boutique (on GKE) uses a `Service` of type `LoadBalancer` named `frontend-external`, which generates a public IP address for the frontend.

If you're deploying this Kustomize component on top of an existing deployment of Online Boutique, you should delete the Service called `frontend-external` that you previously deployed:
```
kubectl delete service frontend-external
```

## Verify that the deployment worked

Check the status of the Google Cloud `ManagedCertificate`.
```bash
kubectl describe managedcertificate frontend-managed-certificate
```

Check that the `frontend` `Ingress` has been assigned the static IP address you created earlier.
```bash
kubectl get ingress
```

Visit your domain on your web browser — first using `http://` to test Online Boutique's services, and then using `https://` to test the HTTPS configuration.
The HTTPS configuration (`https://`) can take a few minutes to provision.

## Related Resources

- [Google Kubernetes Engine: Using Google-managed SSL certificates](https://cloud.google.com/kubernetes-engine/docs/how-to/managed-certs)
