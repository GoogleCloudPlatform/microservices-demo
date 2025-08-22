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

variable "name" {
  type    = string
  default = "online-boutique"
}

variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "az" {
  type    = list(string)
  default = ["ap-south-1a", "ap-south-1b"]
}

variable "aws_profile" {
  type    = string
  default = "xebia-adithya"
}