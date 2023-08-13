resource "aws_iam_role" "eks-cluster-node" {
  name = "eks-cluster-node"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

data "aws_iam_policy_document" "worker_autoscaling" {
  statement {
    sid    = "eksWorkerAutoscalingAll"
    effect = "Allow"

    actions = [
      "autoscaling:DescribeAutoScalingGroups",
      "autoscaling:DescribeAutoScalingInstances",
      "autoscaling:DescribeLaunchConfigurations",
      "autoscaling:DescribeTags",
      "ec2:DescribeLaunchTemplateVersions",
    ]

    resources = ["*"]
  }

  statement {
    sid    = "eksWorkerAutoscalingOwn"
    effect = "Allow"

    actions = [
      "autoscaling:SetDesiredCapacity",
      "autoscaling:TerminateInstanceInAutoScalingGroup",
      "autoscaling:UpdateAutoScalingGroup",
    ]

    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "autoscaling:ResourceTag/kubernetes.io/cluster/${aws_eks_cluster.eks_cluster.id}"
      values   = ["owned"]
    }

    condition {
      test     = "StringEquals"
      variable = "autoscaling:ResourceTag/k8s.io/cluster-autoscaler/enabled"
      values   = ["true"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "workers_autoscaling" {
  policy_arn = aws_iam_policy.worker_autoscaling.arn
  role       = aws_iam_role.eks-cluster-node.name
}

resource "aws_iam_policy" "worker_autoscaling" {
  name_prefix = "eks-worker-autoscaling-${aws_eks_cluster.eks_cluster.id}"
  description = "EKS worker node autoscaling policy for cluster ${aws_eks_cluster.eks_cluster.id}"
  policy      = data.aws_iam_policy_document.worker_autoscaling.json
}



resource "aws_iam_role_policy_attachment" "eks-cluster-node-AmazonEKSWorkerNodePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks-cluster-node.name
}

resource "aws_iam_role_policy_attachment" "eks-cluster-node-AmazonEKS_CNI_Policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks-cluster-node.name
}

resource "aws_iam_role_policy_attachment" "eks-cluster-node-AmazonEC2ContainerRegistryReadOnly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks-cluster-node.name
}

resource "aws_eks_node_group" "eks-cluster-node-group" {
  cluster_name    = aws_eks_cluster.eks_cluster.name
  node_group_name = "eks-cluster-node-group"
  node_role_arn   = aws_iam_role.eks-cluster-node.arn
  subnet_ids      = aws_subnet.project-vpc[*].id
  instance_types = [var.eks_node_instance_type]
  remote_access{
      ec2_ssh_key = var.key_pair_name
  }


  scaling_config {
    desired_size = 2
    max_size     = 3
    min_size     = 2
  }

  depends_on = [
    aws_iam_role_policy_attachment.workers_autoscaling,
    aws_iam_role_policy_attachment.eks-cluster-node-AmazonEKSWorkerNodePolicy,
    aws_iam_role_policy_attachment.eks-cluster-node-AmazonEKS_CNI_Policy,
    aws_iam_role_policy_attachment.eks-cluster-node-AmazonEC2ContainerRegistryReadOnly,
  ]
}