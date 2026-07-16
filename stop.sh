#!/bin/bash

# ============================================
# Online Boutique — Stop Script
# ============================================
# Safely shuts down everything to avoid
# AWS charges. Always run this when done!
# Usage: ./stop.sh
# ============================================

echo ""
echo "================================================"
echo "  Online Boutique — Shutting Down"
echo "================================================"
echo ""

# ── Step 1: Delete frontend service ───────────────
echo "▶ Step 1/4 — Deleting frontend LoadBalancer..."
echo "  (This removes the AWS Load Balancer cleanly)"
kubectl delete -f ~/online-boutique/k8s/frontend.yaml 2>/dev/null || \
  echo "  (frontend already deleted, skipping)"
echo ""

# ── Step 2: Wait for load balancer to be gone ─────
echo "▶ Step 2/4 — Waiting for Load Balancer to be removed..."
echo "  (Waiting 45 seconds...)"
sleep 45

LB=$(aws elb describe-load-balancers --region us-east-1 \
  --query 'LoadBalancerDescriptions[].LoadBalancerName' \
  --output text 2>/dev/null)

if [ -n "$LB" ]; then
  echo "  ⚠️  Load balancer still exists: $LB"
  echo "  Deleting it directly..."
  aws elb delete-load-balancer --region us-east-1 --load-balancer-name "$LB"
  echo "  Waiting 30 more seconds..."
  sleep 30

  # Also clean up the leftover security group
  VPC_ID=$(aws ec2 describe-vpcs --region us-east-1 \
    --filters "Name=tag:Name,Values=online-boutique-vpc" \
    --query 'Vpcs[0].VpcId' --output text 2>/dev/null)

  if [ -n "$VPC_ID" ] && [ "$VPC_ID" != "None" ]; then
    SG_ID=$(aws ec2 describe-security-groups --region us-east-1 \
      --filters "Name=vpc-id,Values=$VPC_ID" "Name=group-name,Values=k8s-elb-*" \
      --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null)
    if [ -n "$SG_ID" ] && [ "$SG_ID" != "None" ]; then
      echo "  Deleting leftover security group: $SG_ID"
      aws ec2 delete-security-group --region us-east-1 --group-id "$SG_ID" 2>/dev/null || true
    fi
  fi
else
  echo "✅ Load balancer is gone!"
fi
echo ""

# ── Step 3: Terraform destroy ─────────────────────
echo "▶ Step 3/4 — Destroying AWS infrastructure..."
echo "  (This takes ~12-15 minutes)"
echo ""
cd ~/online-boutique/terraform-aws
terraform destroy -auto-approve
echo ""
echo "✅ Infrastructure destroyed!"
echo ""

# ── Step 4: Final safety check ────────────────────
echo "▶ Step 4/4 — Running final safety checks..."
echo ""

EKS=$(aws eks list-clusters --region us-east-1 \
  --query 'clusters' --output text 2>/dev/null)
EC2=$(aws ec2 describe-instances --region us-east-1 \
  --query 'Reservations[].Instances[?State.Name==`running`].InstanceId' \
  --output text 2>/dev/null)
ELB=$(aws elb describe-load-balancers --region us-east-1 \
  --query 'LoadBalancerDescriptions[].LoadBalancerName' \
  --output text 2>/dev/null)
VPC=$(aws ec2 describe-vpcs --region us-east-1 \
  --query 'Vpcs[?Tags[?Key==`Name`&&Value==`online-boutique-vpc`]].VpcId' \
  --output text 2>/dev/null)

echo "  EKS clusters:    ${EKS:-none ✅}"
echo "  EC2 instances:   ${EC2:-none ✅}"
echo "  Load balancers:  ${ELB:-none ✅}"
echo "  VPC:             ${VPC:-none ✅}"
echo ""

if [ -z "$EKS" ] && [ -z "$EC2" ] && [ -z "$ELB" ] && [ -z "$VPC" ]; then
  echo "================================================"
  echo "  ✅ ALL CLEAN — No AWS charges running!"
  echo "================================================"
else
  echo "================================================"
  echo "  ⚠️  Some resources may still exist!"
  echo "  Check AWS console or re-run ./stop.sh"
  echo "================================================"
fi
echo ""
