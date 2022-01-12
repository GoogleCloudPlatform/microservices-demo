# Copyright 2021 Paulo Albuquerque
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

variable "app_name" {
  default     = "onlineboutique"
  description = "Application name"
}

variable "project_id" {
  description = "GCP project id"
}

variable "region" {
  description = "GCP region"
}

variable "machine_type" {
  default     = "e2-standard-2"
  description = "Machine type for GKE cluster nodes."
}

variable "preemptible" {
  default     = true
  description = "Preemptible VMs are instances that you can create and run at a much lower price than normal instances. However, Compute Engine might stop (preempt) these instances if it requires access to those resources for other tasks. They're suitable for a GKE development instance."
}

variable "min_node_count" {
  default     = 1
  description = "Minimum number of GKE nodes per zone"
}

variable "max_node_count" {
  default     = 2
  description = "Maximum number of GKE nodes per zone"
}

variable "gke_nodes_cidr" {
  default     = "10.0.0.0/16"
  description = "The IP range in CIDR notation to use for the nodes network. This range will be used for assigning private IP addresses to cluster nodes. This range must not overlap with any other ranges in use within the cluster's network."
}

variable "gke_pods_cidr" {
  default     = "10.1.0.0/16"
  description = "The IP range in CIDR notation to use for the pods network. This range will be used for assigning private IP addresses to pods deployed in the cluster. This range must not overlap with any other ranges in use within the cluster's network."
}

variable "gke_services_cidr" {
  default     = "10.2.0.0/16"
  description = "The IP range in CIDR notation to use for the services network. This range will be used for assigning private IP addresses to services deployed in the cluster. This range must not overlap with any other ranges in use within the cluster's network."
}

variable "gke_master_cidr" {
  default     = "10.3.0.0/28"
  description = "The IP range in CIDR notation to use for the hosted master network. This range will be used for assigning private IP addresses to the cluster master(s) and the ILB VIP. This range must not overlap with any other ranges in use within the cluster's network, and it must be a /28 subnet. "
}