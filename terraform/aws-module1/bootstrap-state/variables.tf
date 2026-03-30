variable "aws_region" {
  description = "AWS region where Terraform state resources are created."
  type        = string
  default     = "eu-south-1"
}

variable "state_bucket_name" {
  description = "Global-unique S3 bucket name for Terraform state."
  type        = string
}

variable "lock_table_name" {
  description = "DynamoDB table name used for Terraform state locking."
  type        = string
  default     = "blackfriday-terraform-locks"
}

variable "tags" {
  description = "Tags applied to backend resources."
  type        = map(string)
  default = {
    ManagedBy = "terraform"
    Project   = "blackfriday-survival"
  }
}
