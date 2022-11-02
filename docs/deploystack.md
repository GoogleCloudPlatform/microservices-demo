## Deploy Online Boutique with DeployStack

The "Open in Google Cloud Shell" button below will use [DeployStack](https://cloud.google.com/shell/docs/cloud-shell-tutorials/deploystack/overview) to deploy Online Boutique to a new Google Kubernetes Engine (GKE) cluster.

<!-- TODO: remove reference to the deploystack-enable branch when it pushes to main -->
<a href="https://ssh.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2FGoogleCloudPlatform%2Fmicroservices-demo&shellonly=true&cloudshell_image=gcr.io/ds-artifacts-cloudshell/deploystack_custom_image" target="_new">
    <img alt="Open in Cloud Shell" src="https://gstatic.com/cloudssh/images/open-btn.svg">
</a>

The button will open up a [Cloud Shell](https://cloud.google.com/shell) session where you will select your Google Cloud project. After project selection, the following will happen automatically:
1. a GKE cluster will be created inside the select project
2. Online Boutique (and its load generator) will be deployed to that cluster
