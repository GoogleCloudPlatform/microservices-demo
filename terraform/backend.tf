terraform {
  backend "s3" {
    bucket         = "induwara-eks-platform-tfstate"
    key            = "eks-platform/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "eks-platform-tfstate-lock"
    encrypt        = true
  }
}