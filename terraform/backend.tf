terraform {
  # Store the state inside a Google Cloud Storage bucket.
  backend "gcs" {
    bucket = "int20h-test-task"
    prefix = "terraform-state"
  }
}
