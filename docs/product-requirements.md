## Product Requirements

This document contains a list of requirements that every change made to this repository should meet.
Every change must:
1. Preserve the golden user journey taken by Kubernetes beginners.
1. Preserve the simplicity of demos.
1. Preserve the simplicity of the GKE quickstart.

### 1. Preserve the golden user journey taken by Kubernetes beginners.

The following statement about Online Boutique should always be true:

> A user outside of Google can deploy Online Boutique's default configuration on a [_kind_ Kubernetes cluster](https://kind.sigs.k8s.io/).

This statement describes the golden user journey that we expect new Kubernetes users to take while onboarding to Online Boutique.

Being able to run Online Boutique on a _kind_ cluster ensures that Online Boutique is free and cloud-agnostic. This is aligned with [Google's mission](https://about.google/) of making information universally accessible and useful. To be specific, Online Boutique should be useful and accessible to developers that are new to Kubernetes.

### 2. Preserve the simplicity of demos.

New changes should not complicate the primary user journey showcased in live demos and tutorials.

Today, the primary user journey is as follows:
1. visit Online Boutique on a web browser
2. select an item from the homepage and add the item to the cart
3. the checkout form is prepopulated with placeholder data (e.g., Shipping Address)
4. the user places the order

### 3. Preserve the simplicity of the GKE quickstart.

New changes should not complicate Online Boutique's [Google Kubernetes Engine (GKE) quickstart](https://github.com/GoogleCloudPlatform/microservices-demo#quickstart-gke).

For instance, a new change should:
* avoid adding an extra step to the GKE quickstart.
* avoid requiring the installation of an additional tool in the GKE quickstart.
* etc.
