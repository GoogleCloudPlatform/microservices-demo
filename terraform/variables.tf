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
  default     = "europe-west1"
}

variable "zone" {
  description = "The GCP zone for the furniture VM."
  type        = string
  default     = "europe-west1-b"
}

variable "ob_network_name" {
  description = "The name of the peer VPC network."
  type        = string
  default     = "online-boutique-vpc"
}

variable "ob_subnet_name" {
  description = "The name of the subnet in the peer VPC."
  type        = string
  default     = "subnet1-europe-west1"
}

variable "ob_gke_pod_range" {
  description = "The CIDR range for the GKE Pods in the peer network."
  type        = list(string)
  default     = ["10.69.128.0/17"]
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
