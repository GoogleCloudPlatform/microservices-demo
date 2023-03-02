# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

variable "gcp_project_id" {
  type        = string
  description = "The GCP project ID to apply this config to"
}

variable "name" {
  type        = string
  description = "Name given to the new GKE cluster"
  default     = "online-boutique"
}

variable "region" {
  type        = string
  description = "Region of the new GKE cluster"
  default     = "us-central1"
}

variable "namespace" {
  type        = string
  description = "Kubernetes Namespace in which the Online Boutique resources are to be deployed"
  default     = "default"
}

variable "filepath_manifest" {
  type        = string
  description = "Path to Online Boutique's Kubernetes resources, written using Kustomize"
  default     = "../kustomize/"
}

variable "memorystore" {
  type        = bool
  description = "If true, Online Boutique's in-cluster Redis cache will be replaced with a Google Cloud Memorystore Redis cache"
}

variable "enable_autopilot" {
  type        = bool
  description = "If true, GKE cluster is provisioned in autopilot mode. Provisioning in autopilot mode ignores values set in 'gke_node_pool' variable"
  default     = true
}

variable "gke_node_pool" {
  type = object({
    machine_type = string

    oauth_scopes = list(string)

    labels = map(string)

    initial_node_count = number

    autoscaling = object({
      min_node_count = number
      max_node_count = number
    })
  })
  nullable    = true
  description = "Defines machine type and size of the default GKE cluster node pool"
  default     = null
}
