module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.34"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  vpc_id     = var.vpc_id
  subnet_ids = var.subnet_ids

  cluster_endpoint_public_access = true
  enable_irsa                    = true

  cluster_addons = {
    coredns    = {}
    kube-proxy = {}
    vpc-cni    = {}
  }

  eks_managed_node_groups = merge(
    {
      default = {
        min_size       = var.node_group_min_size
        max_size       = var.node_group_max_size
        desired_size   = var.node_group_desired_size
        instance_types = var.node_instance_types
        capacity_type  = "ON_DEMAND"

        labels = {
          "workload-tier" = "critical"
          "capacity-type" = "on-demand"
        }
      }
    },
    var.enable_spot_node_group ? {
      spot = {
        min_size       = var.spot_node_group_min_size
        max_size       = var.spot_node_group_max_size
        desired_size   = var.spot_node_group_desired_size
        instance_types = var.spot_node_instance_types
        capacity_type  = "SPOT"

        labels = {
          "workload-tier" = "best-effort"
          "capacity-type" = "spot"
        }

        taints = {
          spot_only = {
            key    = "spot-instance"
            value  = "true"
            effect = "NO_SCHEDULE"
          }
        }
      }
    } : {}
  )

  tags = var.tags
}
