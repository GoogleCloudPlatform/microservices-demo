module "vpc" {
  source = "./modules/vpc"

  name                 = local.vpc_name
  vpc_cidr             = var.vpc_cidr
  availability_zones   = local.azs
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  tags                 = local.tags
}

module "eks" {
  source = "./modules/eks"

  cluster_name                 = local.cluster_name
  cluster_version              = var.cluster_version
  subnet_ids                   = module.vpc.private_subnet_ids
  vpc_id                       = module.vpc.vpc_id
  node_instance_types          = var.node_instance_types
  node_group_min_size          = var.node_group_min_size
  node_group_max_size          = var.node_group_max_size
  node_group_desired_size      = var.node_group_desired_size
  enable_spot_node_group       = var.enable_spot_node_group
  spot_node_instance_types     = var.spot_node_instance_types
  spot_node_group_min_size     = var.spot_node_group_min_size
  spot_node_group_max_size     = var.spot_node_group_max_size
  spot_node_group_desired_size = var.spot_node_group_desired_size
  tags                         = local.tags
}

resource "kubernetes_namespace" "onlineboutique" {
  count = var.enable_cluster_bootstrap ? 1 : 0

  metadata {
    name = "onlineboutique"
    labels = {
      "app.kubernetes.io/part-of" = "blackfriday-survival"
    }
  }
}

resource "kubernetes_namespace" "observability" {
  count = var.enable_cluster_bootstrap ? 1 : 0

  metadata {
    name = "observability"
  }
}

resource "kubernetes_namespace" "argocd" {
  count = var.enable_cluster_bootstrap ? 1 : 0

  metadata {
    name = "argocd"
  }
}

resource "kubernetes_cluster_role" "read_only" {
  count = var.enable_cluster_bootstrap ? 1 : 0

  metadata {
    name = "blackfriday-read-only"
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "services", "endpoints", "events", "namespaces"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = ["apps"]
    resources  = ["deployments", "replicasets", "statefulsets", "daemonsets"]
    verbs      = ["get", "list", "watch"]
  }
}

resource "kubernetes_cluster_role_binding" "read_only_binding" {
  count = var.enable_cluster_bootstrap ? 1 : 0

  metadata {
    name = "blackfriday-read-only-binding"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.read_only[0].metadata[0].name
  }

  subject {
    kind      = "Group"
    name      = "blackfriday-observers"
    api_group = "rbac.authorization.k8s.io"
  }
}

resource "helm_release" "metrics_server" {
  count = var.enable_cluster_bootstrap ? 1 : 0

  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  namespace  = "kube-system"
}

resource "helm_release" "ingress_nginx" {
  count = var.enable_cluster_bootstrap ? 1 : 0

  name             = "ingress-nginx"
  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  namespace        = "ingress-nginx"
  create_namespace = true
}

resource "helm_release" "argocd" {
  count = var.enable_cluster_bootstrap ? 1 : 0

  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = var.argocd_chart_version
  namespace        = kubernetes_namespace.argocd[0].metadata[0].name
  create_namespace = false

  set {
    name  = "server.service.type"
    value = "LoadBalancer"
  }

  set {
    name  = "configs.params.server\\.insecure"
    value = "true"
  }
}
