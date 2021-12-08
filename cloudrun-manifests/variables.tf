variable "path_cred" {
  type        = string
  description = "Path to your API Key from Service Account"

  default = "key/tf-key.json"
}

variable "region" {
  type        = string
  description = "Region to provision resources"

  default = "us-east1"
}

variable "project_id" {
  type        = string
  description = "Region to provision resources"
}
