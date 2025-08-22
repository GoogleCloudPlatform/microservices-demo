# Copyright 2025 Google LLC
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
  public_subnets          = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets         = ["10.0.11.0/24", "10.0.12.0/24"]
  
  enable_nat_gateway      = true
  single_nat_gateway      = true
  enable_dns_support      = true
  enable_dns_hostnames    = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.name}" = "shared"
    "kubernetes.io/role/elb"            = "1"
  }
  
  private_subnet_tags = {
    "kubernetes.io/cluster/${var.name}" = "owned"
    "kubernetes.io/role/internal-elb"   = "1"
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
  subnet_ids                     = module.vpc.private_subnets  # Use private subnets
  enable_irsa                    = true

  enable_cluster_creator_admin_permissions = true
  cluster_enabled_log_types                = ["api", "audit", "authenticator"]
  create_cloudwatch_log_group              = false

  tags = local.tags

  eks_managed_node_groups = {
    general = {
      capacity_type  = "ON_DEMAND"
      instance_types = ["t3.xlarge", "t3a.xlarge"]  # 4 vCPU / 16 GiB - better for heavy workloads
      desired_size   = 4    # Increased from 3
      min_size       = 3    # Increased from 2  
      max_size       = 6    # Room for scaling
      
      labels = { workload = "general" }
      tags   = local.tags
      
      # Enable cluster autoscaler tags
      tags = merge(local.tags, {
        "k8s.io/cluster-autoscaler/enabled"                = "true"
        "k8s.io/cluster-autoscaler/${var.name}"           = "owned"
      })
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
  period              = "86400"
  statistic           = "Maximum"
  threshold           = "30"     # Lowered from $50 to $30 for tighter control
  alarm_description   = "Daily AWS cost exceeded $30 for ${var.name} cluster"
  
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
  timeout    = 3600  # Increased timeout
  wait       = true
  

  values = [yamlencode({
    admissionWebhooks = { patch = { enabled = false } }

grafana = {
  adminUser     = "admin"
  adminPassword = "Admin123!"
  service       = { type = "LoadBalancer" }

  # expose /metrics and protect it with basic auth
  "grafana.ini" = {
    metrics = {
      enabled             = true
    }
  }

  metrics = { enabled = true }

  serviceMonitor = {
    enabled       = true
    path          = "/metrics"
    interval      = "30s"
    scrapeTimeout = "10s"
    labels        = { release = "kube-prom" }
    basicAuth = {
      username = { name = "kube-prom-grafana", key = "admin-user" }
      password = { name = "kube-prom-grafana", key = "admin-password" }
    }
    jobLabel = "app.kubernetes.io/name"
  }

  resources = {
    requests = { cpu = "200m", memory = "512Mi" }
    limits   = { cpu = "500m", memory = "1Gi" }
  }

  persistence = {
    enabled          = true
    size             = "2Gi"
    storageClassName = "gp3"
  }

  additionalDataSources = [
    { name = "Loki",  type = "loki",  access = "proxy", url = "http://loki.logging.svc.cluster.local:3100" },
    { name = "Tempo", type = "tempo", access = "proxy", url = "http://tempo.tracing.svc.cluster.local:3100" }
  ]
}

    prometheus = {
      prometheusSpec = {
        retention      = "24h"  # Increased from 12h
        scrapeInterval = "30s"
        
        # Significantly increased Prometheus resources
        resources = {
          requests = { cpu = "300m", memory = "1Gi" }   # Much higher
          limits   = { cpu = "1", memory = "2Gi" }      # Better limits
        }
        
        storageSpec = {
          volumeClaimTemplate = {
            spec = {
              storageClassName = "gp3"
              accessModes      = ["ReadWriteOnce"]
              resources        = { requests = { storage = "20Gi" } }  # Increased storage
            }
          }
        }
      }
    }

    alertmanager = {
      alertmanagerSpec = {
        resources = {
          requests = { cpu = "50m", memory = "128Mi" }   # Slightly increased
          limits   = { cpu = "200m", memory = "256Mi" }
        }
        storage = {
          volumeClaimTemplate = {
            spec = {
              storageClassName = "gp3"
              accessModes      = ["ReadWriteOnce"]
              resources        = { requests = { storage = "2Gi" } }
            }
          }
        }
      }
    }

    # Optimized component resources
    kubeStateMetrics = {
      resources = {
        requests = { cpu = "100m", memory = "200Mi" }  # Increased
        limits   = { cpu = "300m", memory = "400Mi" }
      }
    }

    prometheusOperator = {
      resources = {
        requests = { cpu = "100m", memory = "200Mi" }  # Increased
        limits   = { cpu = "300m", memory = "400Mi" }
      }
    }

    nodeExporter = {
      resources = {
        requests = { cpu = "50m", memory = "64Mi" }    # Slightly increased
        limits   = { cpu = "100m", memory = "128Mi" }
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
  timeout    = 2400

  values = [yamlencode({
    loki = {
      auth_enabled = false
      
      # Add persistence to Loki
      persistence = {
        enabled      = true
        size         = "10Gi"
        storageClassName = "gp3"
      }
      
      # Resource limits for Loki
      resources = {
        requests = { cpu = "100m", memory = "256Mi" }
        limits   = { cpu = "300m", memory = "512Mi" }
      }
    }
    
    grafana = { enabled = false }
    
    promtail = {
      enabled = true
      resources = {
        requests = { cpu = "50m", memory = "64Mi" }
        limits   = { cpu = "100m", memory = "128Mi" }
      }
    }
  })]

  depends_on = [module.eks, kubernetes_namespace.logging]
}

# ---------------- Traces: Tempo ----------------
resource "helm_release" "tempo" {
  name       = "tempo"
  namespace  = kubernetes_namespace.tracing.metadata[0].name
  repository = "https://grafana.github.io/helm-charts"
  chart      = "tempo"
  timeout    = 2400

  values = [yamlencode({
    # Enable persistence for Tempo
    persistence = {
      enabled = true
      size    = "10Gi"
      storageClassName = "gp3"
    }
    
    # Resource allocation for Tempo
    resources = {
      requests = { cpu = "100m", memory = "256Mi" }
      limits   = { cpu = "300m", memory = "512Mi" }
    }
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

# delay to let ELB DNS publish
resource "time_sleep" "lb_settle" {
  depends_on      = [kubectl_manifest.online_boutique]
  create_duration = "60s"
}

data "kubernetes_service" "grafana" {
  metadata {
    name      = "kube-prom-grafana"
    namespace = "monitoring"
  }
  depends_on = [time_sleep.lb_settle]
}

# keep only this one block
data "kubernetes_service" "frontend" {
  metadata {
    name      = "frontend-external"
    namespace = "default"
  }
  depends_on = [time_sleep.lb_settle]
}