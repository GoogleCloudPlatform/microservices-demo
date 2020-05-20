terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
provider "google" {
  # pin provider to 2.x
  project = var.project
  version = "~> 2.5"
}

# we also use the random provider so let's pin that too
provider "random" {
  version = "~> 2.0"
}

resource "google_project_service" "iam" {
  project = var.project

  service = "iam.googleapis.com"

  disable_dependent_services = true
}

resource "google_project_service" "compute" {
  project = var.project

  service = "compute.googleapis.com"

  disable_dependent_services = true
}

resource "google_project_service" "clouddebugger" {
  project = var.project

  service = "clouddebugger.googleapis.com"

  disable_dependent_services = true
}


resource "google_project_service" "cloudtrace" {
  project = var.project

  service = "cloudtrace.googleapis.com"

  disable_dependent_services = true
}

resource "google_project_service" "errorreporting" {
  project = var.project

  service = "clouderrorreporting.googleapis.com"

  disable_dependent_services = true
}

# Enable GKE in the project we created. If you look at the docs you might see
# the `google_project_services` resource which allows you to specify a list of
# resources to enable. This seems like a good idea but there's a gotcha: to use
# that resource you have to specify a comprehensive list of services to be
# enabled for your project. Otherwise it will disable services you might be
# using elsewhere.
#
# For that reason, we use the single service option instead since it allows us
# granular control.
resource "google_project_service" "gke" {
  # This could just as easily reference `random_id.project.dec` but generally
  # you want to dereference the actual object you're trying to interact with.
  #
  # You'll see this line in every resource we create from here on out. This is
  # necessary because we didn't configure the provider with a project because
  # the project didn't exist yet. This could be refactored such that the project
  # was created outside of terraform, the provider configured with the project,
  # and then we don't have to specify this on every resource any more.
  #
  # Anyway, expect to see a lot more of these. I won't explain every time.
  project = var.project

  # the service URI we want to enable
  service = "container.googleapis.com"

  disable_dependent_services = true
}

# Let's create the GKE cluster! This one's pretty complicated so buckle up.

# This is another example of the random provider. Here we're using it to pick a
# zone in us-central1 at random.
resource "random_shuffle" "zone" {
  input = ["us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"]

  # Seeding the RNG is technically optional but while building this we
  # found that it only ever picked `us-central-1c` unless we seeded it. Here
  # we're using the ID of the project as a seed because it is unique to the
  # project but will not change, thereby guaranteeing stability of the results.
  seed = var.project
}

# First we create the cluster. If you're wondering where all the sizing details
# are, they're below in the `google_container_node_pool` resource. We'll get
# back to that in a minute.
#
# One thing to note here is the name of the resource ("gke") is only used
# internally, for instance when you're referencing the resource (eg
# `google_container_cluster.gke.id`). The actual created resource won't know
# about it, and in fact you can specify the name for that in the resource
# itself.
#
# Finally, there are many, many other options available. The resource below
# replicates what the Hipster Shop README creates. If you want to see what else
# is possible, check out the docs: https://www.terraform.io/docs/providers/google/r/container_cluster.html
resource "google_container_cluster" "gke" {
  project = var.project

  # Here's how you specify the name
  name = "demo-cluster"

  # Set the zone by grabbing the result of the random_shuffle above. It
  # returns a list so we have to pull the first element off. If you're looking
  # at this and thinking "huh terraform syntax looks a clunky" you are NOT WRONG
  zone = element(random_shuffle.zone.result, 0)

  # Using an embedded resource to define the node pool. Another
  # option would be to create the node pool as a separate resource and link it
  # to this cluster. There are tradeoffs to each approach.
  #
  # The embedded resource is convenient but if you change it you have to tear
  # down the entire cluster and rebuild it. A separate resource could be
  # modified independent of the cluster without the cluster needing to be torn
  # down.
  #
  # For this particular case we're not going to be modifying the node pool once
  # it's deployed, so it makes sense to accept the tradeoff for the convenience
  # of having it inline.
  #
  # Many of the paramaters below are self-explanatory so I'll only call out
  # interesting things.
  node_pool {
    node_config {
      oauth_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"  
      ]

      labels = {
        environment = "dev",
        cluster = "demo-cluster"   
      }
    }
    
    initial_node_count = 5

    autoscaling {
      min_node_count = 3
      max_node_count = 10
    }

    management {
      auto_repair  = true
      auto_upgrade = true
    }
  }

  # Specifies the use of "new" Stackdriver logging and monitoring
  # https://cloud.google.com/kubernetes-engine-monitoring/
  logging_service = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"

  # Stores the zone of created gke cluster
  provisioner "local-exec" {
    command = "gcloud config set compute/zone ${element(random_shuffle.zone.result, 0)}"
  }
  
  # add a hint that the service resource must be created (i.e., the service must
  # be enabled) before the cluster can be created. This will not address the
  # eventual consistency problems we have with the API but it will make sure
  # that we're at least trying to do things in the right order.
  depends_on = [google_project_service.gke]
}

# Set current project 
resource "null_resource" "current_project" {
  provisioner "local-exec" {
    command = "gcloud config set project ${var.project}"
  }
}

# Setting kubectl context to currently deployed GKE cluster
resource "null_resource" "set_gke_context" {
  provisioner "local-exec" {
    command = "gcloud container clusters get-credentials demo-cluster --zone ${element(random_shuffle.zone.result, 0)} --project ${var.project}"
  }

  depends_on = [
    google_container_cluster.gke, 
    null_resource.current_project
  ]
}

# Deploy microservices into GKE cluster 
resource "null_resource" "deploy_services" {
  provisioner "local-exec" {
    command = "kubectl apply -f ..//release//kubernetes-manifests.yaml"
  }

  depends_on = [null_resource.set_gke_context]
}

# There is no reliable way to do deployment verification with kubernetes
# For the purposes of Sandbox, we can mitigate by waiting a few sec to ensure kubectl apply completes
resource "null_resource" "delay" {
  provisioner "local-exec" {
    command = "sleep 5"
  }
  triggers = {
    "before" = "${null_resource.deploy_services.id}"
  }
}

