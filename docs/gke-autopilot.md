# Using GKE Autopilot

## Overview

GKE provides two [modes of operation]:

- **Autopilot mode**, which is designed to reduce the operational cost of
managing clusters, apply best security practices to harden your clusters, and
optimize them for production to yield higher workload availability.

- **Standard mode** in which you are responsible for provisioning, managing, and
monitoring the nodes of your physical cluster.

In this tutorial, we'll demonstrate how to deploy the Online Boutique
microservices demo using GKE Autopilot mode. You'll see firsthand how using
Autopilot mode is simple and straightforward.

In the final section, we'll explain the benefits of using GKE Autopilot in more
detail.

## Getting Started

Getting started is easy and we'll show two ways to create your GKE Autopilot
cluster.

- Using Cloud Console.
- Using the command line.

Once you have a created a cluster, you can go to the section on [Deploying the
demo].

> Whether you use Cloud Console or the command line to create the cluster, you
will still need to use `kubectl` at the command line to deploy the application.
>
> The instructions assume you already have [Google Cloud SDK (gcloud)] and
[kubectl] (which can be optionally installed as a `gcloud` component).
>
> If you prefer, you can use [Cloud Shell] for a hosted terminal environment
that already has these tools installed for you.


### Select or create a project using Cloud Console

1. In the Google Cloud Console, go to the [project selector] page. Either select
an existing project or create a new one.

1. Next, using the left navigation menu, choose **Kubernetes Engine**.

1. If prompted, click to **ENABLE** the Kubernetes API.

1. On the **Kubernetes Engine Clusters** page, click the **CREATE** button.

1. The **Create Cluster** dialog will prompt you to select a cluster mode. Click
the **CONFIGURE** button.

1. You will be prompted to **Create an Autopilot cluster**. You can accept all
the defaults.

1. Once the cluster is created, click on the name link to go to the cluster
**DETAILS** tab. Click the **CONNECT** button to get the command you'll use to
connect to the cluster using the command line. Copy the command and paste it
to your command line and press enter.

Now you're ready to deploy the demo.

### Select or create a project using the command line

The following steps are purely administrative. You need to log in and identify
the project you want to work with.

```text
gcloud auth login
```

Then either choose an existing project or create a new one.

#### Select an existing project

```text
PROJECT_ID=my-project-id
gcloud services enable container.googleapis.com --project $PROJECT_ID
```

This assumes you have billing set for the project. If not, see the next section
and look for the `gcloud beta billing` command to link billing up.

#### Create a new project

> You will need to know your [billing ID].

```text
PROJECT_NAME=my-project-name
gcloud projects create $PROJECT_NAME
```

The output will print the assigned project ID associated with the project name.
Use the following command to get the project ID and store it to `PROJECT_ID`:

```text
export PROJECT_ID=$(gcloud projects list --filter NAME=$PROJECT_NAME --format='value(PROJECT_ID)')
```

#### Set billing for the project.

```text
gcloud beta billing projects link tonypujals-autopilot-demo --billing-account=XXXXXX-XXXXXX-XXXXXX
```

#### Enable the containers API for your project

```text
gcloud services enable container.googleapis.com --project $PROJECT_ID
```

#### Create the Autopilot cluster

By creating an Autopilot cluster (with `create-auto`) you only need to give the
cluster a name. You can't specify any options that configure cluster nodes.

```text
gcloud beta container clusters create-auto microservices-demo
```

Output:

```text
WARNING: Starting with version 1.18, clusters will have shielded GKE nodes by default.
WARNING: The Pod address range limits the maximum size of the cluster. Please refer to https://cloud.google.com/kubernetes-engine/docs/how-to/flexible-pod-cidr to learn how to optimize IP address allocation.
WARNING: Starting with version 1.19, newly created clusters and node-pools will have COS_CONTAINERD as the default node image when no image type is specified.
Creating cluster auto-microservices-demo in us-central1...done.
Created [https://container.googleapis.com/v1beta1/projects/my-project/zones/us-central1/clusters/microservices-demo].
To inspect the contents of your cluster, go to: https://console.cloud.google.com/kubernetes/workload_/gcloud/us-central1/microservices-demo?project=my-project
kubeconfig entry generated for microservices-demo.
NAME                       LOCATION     MASTER_VERSION  MASTER_IP     MACHINE_TYPE  NODE_VERSION    NUM_NODES  STATUS
microservices-demo         us-central1  1.20.8-gke.900  35.223.7.213  e2-medium     1.20.8-gke.900  3          RUNNING
```
You can safely ignore the warnings. These simply indicate the cluster was
created with default values. Other than network settings, these values can't be
overridden anyway for an Autopilot cluster.

You can see that the cluster is initially configured with three
conservatively-sized machines for the nodes. These nodes are distributed across
three zones in the `us-central1` region.

## Deploying the demo

Now that you have an Autopilot cluster, you can deploy the Online Boutique using
Kubernetes:

```text
kubectl apply -f release/kubernetes-manifests.yaml
```

The output should look similar to deploying the cluster in standard mode, with a
notable exception: you may see warnings similar to this:

```text
Warning: Autopilot increased resource requests for Deployment default/checkoutservice to meet requirements. See http://g.co/gke/autopilot-resources.
deployment.apps/checkoutservice created
service/checkoutservice created
```

Again, this is nothing to be concerned about, but it is notable that Autopilot
will automatically adjust pod resource requirements to fit within [allowable
resource ranges].

Once the application has finished deploying, you can get the public IP with the
following command:

```text
PUBLIC_IP=$(kubectl get service frontend-external -o jsonpath="{.status.loadBalancer.ingress[0].ip}")
```

## Wrapup: Why use GKE Autopilot mode?

Most developers are familiar with **standard mode** since **Autopilot mode** is
a new mode that launched in early 2021.

GKE Autopilot mode provides a *nodeless* experience that optimizes cluster node
resource provisioning so that you can focus on your workloads instead of
infrastructure and only pay for the pods you actually use. As application load
increases, your Autopilot cluster will automatically scale as necessary.
However, if any node resources provisioned to ensure availability are being
underutilized, there's no need for concern -- you only pay consumption costs for
pods that are actually running.

For many customers, not only does this translate to a reduction in operations
overhead, but they may also realize price efficiencies from optimized clusters
that reduce costs incurred through over-provisioning node resources.

Another significant advantage is that **Autopilot mode** generally allows
developers to focus on pure Kubernetes configuration, not vendor-specfic
infrastructure configuration. This helps them to become immediately productive
with what they've learned about Kubernetes without also having to learn about
specific vendor machine types and a separate API for creating them, accelerating
productivity.

Almost any kind of workload that you can run under GKE standard mode will run
under Autopilot mode. In general, the control over physical nodes that you by
definition trade for Autopilot provisioned nodes, means that you can't ssh into
nodes, nor specify node selectors and affinity (you can still do this for zones,
just not for specific nodes), nor run privileged pods.

These and similar types of [restrictions] that typically apply to the class of
administrative workloads necessary for self-managed clusters are no longer
necessary since Google assumes this responsibility, providing customers with up
to a 99.9% [SLA] for a multiple zone configuration. 

If at some point you determine that you require the full range of control
offered by GKE standard mode, you will not need to make any changes to your
application nor existing configuration, since you're not migrating from a
different type of container orchestration platform to another, or different type
of programming model. You can always create a new standard mode cluster on GKE
and configure your own nodes the typical way (perhaps leveraging Terraform), and
redeploy your workloads to the new cluster.

### Rightsizing clusters is not easy

Choosing the optimal size for your cluster nodes is challenging and requires
constant monitoring to ensure you're not under- or over-provisioning your
infrastructure. On one hand, your app may perform poorly under load and on the
other, you are almost certainly overpaying for resources that are being
underutilized.

If you deploy the Online Boutique using the guidance for standard mode and
compare cluster resources with what Autopilot configured, the difference is
quite dramatic.

![Comparing initial cluster sizes](./img/gke-clusters-comparison.png)

You can test the application at both public addresses to confirm
they work as expected, and you can be confident that Autopilot will increase
cluster resources if it detects that your application requires that.

Unless you have special requirements, we believe that GKE Autopilot is the best
way for most customers to run their Kubernetes workloads in the Cloud.

<!-- Reference links -->

[allowable resource ranges]:
https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview#allowable_resource_ranges

[billing id]:
https://console.cloud.google.com/billing

[cloud shell]:
https://cloud.google.com/shell

[deploying the demo]:
#deploying-the-demo

[Google Cloud SDK (gcloud)]:
https://cloud.google.com/sdk/docs/install

[kubectl]:
https://kubernetes.io/docs/tasks/tools/

[restrictions]:
https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview

[modes of operation]:
https://cloud.google.com/kubernetes-engine/docs/concepts/kubernetes-engine-overview#modes

[project selector]:
https://console.cloud.google.com/projectselector2/home/dashboard

[sla]:
https://cloud.google.com/kubernetes-engine/sla
