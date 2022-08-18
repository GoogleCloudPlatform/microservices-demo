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

# Create the Memorystore (redis) instance
resource "google_redis_instance" "redis-cart" {
  name           = "redis-cart"
  memory_size_gb = 1
  region         = var.region

  # count specifies the number of instances to create;
  # if var.memorystore is true then the resource is enabled
  count          = var.memorystore ? 1 : 0

  redis_version  = "REDIS_6_X"
  project        = var.gcp_project_id

  depends_on = [
    module.enable_google_apis
  ]
}

# Edit contents of Memorystore kustomization.yaml file to target new Memorystore (redis) instance
resource "null_resource" "kustomization-update" {
  provisioner "local-exec" {
    interpreter = ["bash", "-exc"]
    command     = "sed -i \"s/REDIS_IP/${google_redis_instance.redis-cart[0].host}/g\" ../kustomize/components/memorystore/kustomization.yaml"
  }

  # count specifies the number of instances to create;
  # if var.memorystore is true then the resource is enabled
  count          = var.memorystore ? 1 : 0

  depends_on = [
    resource.google_redis_instance.redis-cart
  ]
}
