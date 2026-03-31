locals {
  environment_name = terraform.workspace
  project_name_with_suffix = endswith(
    lower(var.project_name),
    lower("-${var.name_suffix}")
  ) ? var.project_name : "${var.project_name}-${var.name_suffix}"
  name_prefix  = local.environment_name == "default" ? local.project_name_with_suffix : "${local.project_name_with_suffix}-${local.environment_name}"
  cluster_name = local.name_prefix
  vpc_name     = local.name_prefix

  azs = slice(data.aws_availability_zones.available.names, 0, 3)

  tags = merge(var.tags, {
    Project     = local.project_name_with_suffix
    Environment = local.environment_name
    ManagedBy   = "terraform"
  })
}
