locals {
  tags = { 
    Project = "OnlineBoutique", 
    Owner = "Adithya", 
    TTL = "today",
    Environment = "demo",
    CostCenter = "RD"
  }
}

# ---------------- VPC ----------------
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name                    = var.name
  cidr                    = "10.0.0.0/16"
  azs                     = var.az
  public_subnets          = ["10.0.0.0/24", "10.0.1.0/24"]
  enable_nat_gateway      = false
  enable_dns_support      = true
  enable_dns_hostnames    = true
  map_public_ip_on_launch = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.name}" = "owned"
    "kubernetes.io/role/elb"            = "1"
  }

  tags = local.tags

}

# ---------------- EKS ----------------
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name                   = var.name
  cluster_version                = "1.29"
  cluster_endpoint_public_access = true
  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.public_subnets
  enable_irsa                    = true

  enable_cluster_creator_admin_permissions = true
  cluster_enabled_log_types                = ["api", "audit", "authenticator"]
  create_cloudwatch_log_group              = false

  tags = local.tags

  eks_managed_node_groups = {
    spot = {
      capacity_type  = "ON_DEMAND"
      instance_types = ["t3.large", "t3a.large"]    # 2 vCPU / 8 GiB
      desired_size   = 3
      min_size       = 2
      max_size       = 5                            # Increased from 4 to 5
      labels         = { workload = "general" }
      tags           = local.tags
    }
  }
}

# ---------------- Cost Monitoring ----------------
resource "aws_cloudwatch_metric_alarm" "daily_cost_alert" {
  alarm_name          = "daily-cost-alert-${var.name}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "86400"  # 24 hours
  statistic           = "Maximum"
  threshold           = "50"     # Alert if > $50/day
  alarm_description   = "Daily AWS cost exceeded $50 for ${var.name} cluster"
  
  dimensions = {
    Currency = "USD"
  }

  tags = local.tags
}

# ------------- EBS CSI addon -------------
resource "aws_eks_addon" "ebs_csi" {
  cluster_name                = module.eks.cluster_name
  addon_name                  = "aws-ebs-csi-driver"
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"
  service_account_role_arn    = aws_iam_role.ebs_csi_irsa.arn
  tags                        = local.tags
  depends_on                  = [module.eks, aws_iam_role_policy_attachment.ebs_csi_attach]
}



# ------- Standard StorageClass alias (for PVCs that request it) -------
resource "kubernetes_storage_class_v1" "standard_alias" {
  metadata { name = "standard" }
  storage_provisioner   = "ebs.csi.aws.com"
  reclaim_policy        = "Delete"
  volume_binding_mode   = "WaitForFirstConsumer"
  allow_volume_expansion = true
  parameters = { type = "gp3", fsType = "ext4" }
  depends_on = [aws_eks_addon.ebs_csi]
}

# ------- Default gp3 StorageClass (CSI) -------
resource "kubernetes_storage_class_v1" "gp3" {
  metadata {
    name = "gp3"
    annotations = {
      "storageclass.kubernetes.io/is-default-class" = "true"
    }
  }
  storage_provisioner    = "ebs.csi.aws.com"
  reclaim_policy         = "Delete"
  volume_binding_mode    = "WaitForFirstConsumer"
  allow_volume_expansion = true
  parameters = {
    type   = "gp3"
    fsType = "ext4"
  }
  depends_on = [aws_eks_addon.ebs_csi]
}

# ---- IRSA for EBS CSI ----
data "aws_iam_policy_document" "ebs_csi_trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"
    principals { 
      type        = "Federated" 
      identifiers = [module.eks.oidc_provider_arn] 
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(module.eks.cluster_oidc_issuer_url, "https://", "")}:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "${replace(module.eks.cluster_oidc_issuer_url, "https://", "")}:sub"
      values   = ["system:serviceaccount:kube-system:ebs-csi-controller-sa"]
    }
  }
}

resource "aws_iam_role" "ebs_csi_irsa" {
  name               = "${var.name}-ebs-csi-irsa"
  assume_role_policy = data.aws_iam_policy_document.ebs_csi_trust.json
  tags               = local.tags
}

resource "aws_iam_role_policy_attachment" "ebs_csi_attach" {
  role       = aws_iam_role.ebs_csi_irsa.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}

# ---------------- Namespaces ----------------
resource "kubernetes_namespace" "monitoring" {
  metadata { name = "monitoring" }
  depends_on = [module.eks]
}
resource "kubernetes_namespace" "logging" {
  metadata { name = "logging" }
  depends_on = [module.eks]
}
resource "kubernetes_namespace" "tracing" {
  metadata { name = "tracing" }
  depends_on = [module.eks]
}

resource "helm_release" "kps" {
  name       = "kube-prom"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  timeout    = 2400
  wait       = true

  values = [yamlencode({
    admissionWebhooks = { patch = { enabled = false } }

    grafana = {
      adminUser     = "admin"
      adminPassword = "Admin123!"
      service       = { type = "LoadBalancer" }
      resources = {
        requests = { cpu = "50m", memory = "128Mi" }
        limits   = { cpu = "200m", memory = "256Mi" }
      }
      additionalDataSources = [
        { name = "Loki", type = "loki", access = "proxy", url = "http://loki.logging.svc.cluster.local:3100" },
        { name = "Tempo", type = "tempo", access = "proxy", url = "http://tempo.tracing.svc.cluster.local:3100" }
      ]
    }

    prometheus = {
      prometheusSpec = {
        retention      = "12h"
        scrapeInterval = "30s"
        resources = {
          requests = { cpu = "50m", memory = "200Mi" }
          limits   = { cpu = "200m", memory = "400Mi" }
        }
        storageSpec = {
          volumeClaimTemplate = {
            spec = {
              storageClassName = "gp3"
              accessModes      = ["ReadWriteOnce"]
              resources        = { requests = { storage = "5Gi" } }
            }
          }
        }
      }
    }

    alertmanager = {
      alertmanagerSpec = {
        resources = {
          requests = { cpu = "25m", memory = "64Mi" }
          limits   = { cpu = "100m", memory = "128Mi" }
        }
        storage = {
          volumeClaimTemplate = {
            spec = {
              storageClassName = "gp3"
              accessModes      = ["ReadWriteOnce"]
              resources        = { requests = { storage = "1Gi" } }
            }
          }
        }
      }
    }

    kubeStateMetrics = {
      resources = {
        requests = { cpu = "50m", memory = "120Mi" }
        limits   = { cpu = "150m", memory = "250Mi" }
      }
    }

    prometheusOperator = {
      resources = {
        requests = { cpu = "50m", memory = "100Mi" }
        limits   = { cpu = "150m", memory = "200Mi" }
      }
    }

    nodeExporter = {
      resources = {
        requests = { cpu = "15m", memory = "30Mi" }
        limits   = { cpu = "50m", memory = "60Mi" }
      }
    }
  })]

  depends_on = [
    module.eks,
    kubernetes_namespace.monitoring,
    aws_eks_addon.ebs_csi,
    kubernetes_storage_class_v1.gp3
  ]
}

# ---------------- Metrics Server ----------------
resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  namespace  = "kube-system"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  version    = "3.13.0"  # Updated to latest stable version
  wait       = true
  
  values = [yamlencode({
    args = [
      "--kubelet-preferred-address-types=InternalIP,Hostname,InternalDNS,ExternalDNS,ExternalIP",
      "--kubelet-insecure-tls"
    ]
  })]
  
  depends_on = [module.eks]
}

# --------------- Logs: Loki + Promtail ---------------
resource "helm_release" "loki_stack" {
  name       = "loki"
  namespace  = kubernetes_namespace.logging.metadata[0].name
  repository = "https://grafana.github.io/helm-charts"
  chart      = "loki-stack"

  values = [yamlencode({
    loki     = { auth_enabled = false }
    grafana  = { enabled = false }
    promtail = { enabled = true }
  })]

  depends_on = [module.eks, kubernetes_namespace.logging]
}

# ---------------- Traces: Tempo ----------------
resource "helm_release" "tempo" {
  name       = "tempo"
  namespace  = kubernetes_namespace.tracing.metadata[0].name
  repository = "https://grafana.github.io/helm-charts"
  chart      = "tempo"

  values = [yamlencode({
    persistence = { enabled = false }
  })]

  depends_on = [module.eks, kubernetes_namespace.tracing]
}

# --------------- OTel Collector ----------------
resource "helm_release" "otel" {
  name       = "otel-collector"
  namespace  = kubernetes_namespace.tracing.metadata[0].name
  repository = "https://open-telemetry.github.io/opentelemetry-helm-charts"
  chart      = "opentelemetry-collector"
  timeout    = 2400
  wait       = true

  values = [yamlencode({
    mode         = "deployment"
    replicaCount = 1
    image        = { repository = "otel/opentelemetry-collector-contrib" }  # This is required!
    
    # Let the Helm chart use its default config, just override the Tempo endpoint
    config = {
      exporters = {
        otlp = { 
          endpoint = "tempo.tracing.svc.cluster.local:4317", 
          tls = { insecure = true } 
        }
      }
    }
  })]

  depends_on = [module.eks, kubernetes_namespace.tracing, helm_release.tempo]
}

# ---------- Beyla eBPF auto-instrumentation ----------
resource "helm_release" "beyla" {
  name       = "beyla"
  namespace  = kubernetes_namespace.tracing.metadata[0].name
  repository = "https://grafana.github.io/helm-charts"
  chart      = "beyla"
  timeout    = 2400  # Increase from default 900s to 30 minutes
  wait       = true

  values = [yamlencode({
    config = {
      discovery = {
        instrument = [
          { k8s_namespace = "default" }
        ]
      }
      otel = {
        traces_export = {
          endpoint = "http://otel-collector.tracing.svc.cluster.local:4318"
        }
        service_name = "beyla-ebpf"
      }
    }
  })]

  depends_on = [module.eks, kubernetes_namespace.tracing, helm_release.otel]
}

# ------- Deploy Online Boutique (Split Multi-Doc) -------
data "kubectl_file_documents" "online_boutique" {
  content = file("${path.module}/../../release/kubernetes-manifests.yaml")
}

resource "kubectl_manifest" "online_boutique" {
  for_each          = data.kubectl_file_documents.online_boutique.manifests
  yaml_body         = each.value
  server_side_apply = true
  apply_only        = true
  wait_for_rollout  = false
  
  depends_on = [
    module.eks,
    aws_eks_addon.ebs_csi,
    kubernetes_storage_class_v1.gp3,
    helm_release.kps,
    helm_release.loki_stack,
    helm_release.tempo,
    helm_release.otel,
    helm_release.beyla
  ]
}


# ---------------- Read LB hostnames ----------------
data "kubernetes_service" "grafana" {
  metadata {
    name      = "kube-prom-grafana"
    namespace = "monitoring"
  }
  depends_on = [helm_release.kps]
}

data "kubernetes_service" "frontend" {
  metadata {
    name      = "frontend-external"
    namespace = "default"
  }
  depends_on = [kubectl_manifest.online_boutique]
}
