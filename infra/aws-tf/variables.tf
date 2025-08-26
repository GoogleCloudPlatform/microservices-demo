# Copyright 2025 Google LLC
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

variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "aws_profile" {
  type    = string
  default = "xebia"
}

variable "name" {
  type    = string
  default = "online-boutique"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "cluster_version" {
  type    = string
  default = "1.30"
}

variable "tags" {
  type = map(string)
  default = {
    Project     = "OnlineBoutique"
    Owner       = "Xebia-team"
    TTL         = "today"
    Environment = "demo"
    CostCenter  = "RD"
  }
}

variable "node_instance_types" {
  type    = list(string)
  default = ["t3.medium", "t3.large", "t3a.medium", "t2.medium"]
}

variable "desired_size" {
  type    = number
  default = 2
}

variable "min_size" {
  type    = number
  default = 2
}

variable "max_size" {
  type    = number
  default = 4
}

variable "capacity_type" {
  type    = string
  default = "SPOT" # or "ON_DEMAND"
}
