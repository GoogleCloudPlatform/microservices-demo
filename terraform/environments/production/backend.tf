# forgeteam: GCS bucket for Terraform backend
terraform {
  backend "gcs" {
    bucket = "forgeteam-tfstate-1771882722"
    prefix = "state/production"
  }
}
