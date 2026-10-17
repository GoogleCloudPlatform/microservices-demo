# 🛑 Hướng Dẫn Destroy & Re-create Hạ Tầng AWS (Online Boutique)

> **Mục tiêu:** Hướng dẫn quy trình tiêu hủy (destroy) hạ tầng vào cuối ngày làm việc nhằm tiết kiệm chi phí tối đa (~60-70% ngân sách Cloud), đồng thời cung cấp các bước bật lại (re-deploy) nhanh chóng vào sáng hôm sau mà không gặp lỗi phụ thuộc (`DependencyViolation`).

---

## 1. Tại Sao Không Thể Chạy `terraform destroy` Ngay Lập Tức?

Trong kiến trúc Kubernetes trên AWS (EKS), có 2 nhóm tài nguyên:
1. **Tài nguyên do Terraform quản lý:** VPC, Subnets, Internet/NAT Gateway, Route Tables, EKS Cluster, Node Groups, ElastiCache Redis, IAM Roles.
2. **Tài nguyên do Kubernetes Controller tạo động ngoài tầm Terraform (Out-of-band):**
   - Service `frontend-external` (`type: LoadBalancer`) → Tạo **Network Load Balancer (NLB)**.
   - Service `argocd-server` (`type: LoadBalancer`) → Tạo **Classic ELB**.
   - Các Target Groups, Security Groups (`k8s-traffic-...`, `k8s-elb-...`) và các **Elastic Network Interfaces (ENIs)** gắn vào public/private subnets.

> [!WARNING]
> **Quy tắc vàng:** Nếu chạy `terraform destroy` ngay, Terraform sẽ xóa cụm EKS trước. Khi cụm EKS bị xóa, Kubernetes Controller không còn tồn tại để dọn dẹp các Load Balancer trên AWS.
> 
> Hậu quả: Các Load Balancer và ENI bị **"mồ côi" (orphaned)** nằm kẹt trong Subnet. AWS sẽ từ chối xóa Subnet và VPC với lỗi `DependencyViolation`, khiến tiến trình destroy bị treo suốt 20–30 phút và thất bại.

---

## 2. Quy Trình Chuẩn (SOP) Destroy Cuối Ngày (Chỉ mất 5–7 phút)

Thực hiện đúng thứ tự **2 bước** sau:

### Bước 1: Dọn dẹp Load Balancers trên Kubernetes (khi EKS còn sống)

Mở PowerShell tại máy của bạn và chạy:

```powershell
# 1. Xóa các ứng dụng ArgoCD
kubectl delete application online-boutique-dev aws-lb-controller cluster-autoscaler -n argocd --timeout=60s

# 2. Xóa namespace online-boutique (xóa Service frontend-external để AWS thu hồi NLB)
kubectl delete ns online-boutique --timeout=90s

# 3. Gỡ cài đặt ArgoCD (xóa Service argocd-server để AWS thu hồi Classic ELB)
helm uninstall argocd -n argocd
kubectl delete ns argocd --timeout=60s
```

**Kiểm tra xác nhận các Load Balancer đã được thu hồi hoàn toàn:**
```powershell
aws elbv2 describe-load-balancers --region ap-southeast-1 --query "LoadBalancers[*].LoadBalancerName"
aws elb describe-load-balancers --region ap-southeast-1 --query "LoadBalancerDescriptions[*].LoadBalancerName"
```
*(Cả 2 lệnh trên trả về `[]` nghĩa là các ELB/NLB và ENI đã được giải phóng sạch sẽ).*

---

### Bước 2: Chạy Terraform Destroy

Chuyển vào thư mục môi trường dev và chạy lệnh destroy:

```powershell
cd d:\online-boutique\online-boutique-app\terraform-aws\environments\dev
terraform destroy -auto-approve
```

Terraform sẽ xóa toàn bộ EKS, Node Groups, ElastiCache Redis, NAT Gateway, EIP và VPC trơn tru 100% mà không bị bất kỳ lỗi phụ thuộc nào.

---

## 3. Script Dọn Dẹp Khẩn Cấp (Khi Đã Lỡ Bị Kẹt Do Xóa EKS Trước)

Nếu bạn đã lỡ bấm `terraform destroy` trước khi dọn dẹp Service K8s khiến EKS đã mất mà VPC bị kẹt, hãy chạy script Python sau để cưỡng chế xóa sạch toàn bộ tài nguyên mồ côi:

```powershell
python -c "
import subprocess, json

region = 'ap-southeast-1'

# 1. Xóa tất cả NLB/ALB còn sót
try:
    cmd = ['aws', 'elbv2', 'describe-load-balancers', '--region', region, '--query', 'LoadBalancers[*].LoadBalancerArn', '--output', 'json']
    arns = json.loads(subprocess.check_output(cmd))
    for arn in arns:
        print(f'Deleting ELBv2: {arn}')
        subprocess.call(['aws', 'elbv2', 'delete-load-balancer', '--load-balancer-arn', arn, '--region', region])
except Exception as e:
    print('ELBv2 check:', e)

# 2. Xóa Classic ELB còn sót
try:
    cmd = ['aws', 'elb', 'describe-load-balancers', '--region', region, '--query', 'LoadBalancerDescriptions[*].LoadBalancerName', '--output', 'json']
    names = json.loads(subprocess.check_output(cmd))
    for name in names:
        print(f'Deleting Classic ELB: {name}')
        subprocess.call(['aws', 'elb', 'delete-load-balancer', '--load-balancer-name', name, '--region', region])
except Exception as e:
    print('Classic ELB check:', e)

# 3. Xóa Target Groups k8s
try:
    cmd = ['aws', 'elbv2', 'describe-target-groups', '--region', region, '--query', 'TargetGroups[*].[TargetGroupName,TargetGroupArn]', '--output', 'json']
    tgs = json.loads(subprocess.check_output(cmd))
    for name, arn in tgs:
        if 'k8s-' in name:
            print(f'Deleting TG: {name}')
            subprocess.call(['aws', 'elbv2', 'delete-target-group', '--target-group-arn', arn, '--region', region])
except Exception as e:
    print('TG check:', e)

# 4. Xóa Security Groups k8s
try:
    cmd = ['aws', 'ec2', 'describe-security-groups', '--region', region, '--filters', 'Name=group-name,Values=k8s-*', '--query', 'SecurityGroups[*].GroupId', '--output', 'json']
    sgs = json.loads(subprocess.check_output(cmd))
    for sg in sgs:
        print(f'Deleting SG: {sg}')
        subprocess.call(['aws', 'ec2', 'delete-security-group', '--group-id', sg, '--region', region])
except Exception as e:
    print('SG check:', e)

print('Clean up completed! Now you can re-run terraform destroy.')
"
```

Sau khi script chạy xong, bạn chỉ cần gõ lại `terraform destroy -auto-approve` là VPC sẽ bị xóa hoàn tất.

---

## 4. Quy Trình Bật Lại Hạ Tầng (Re-Deploy Sáng Hôm Sau)

Vào đầu ngày mới khi bắt đầu làm việc, chỉ cần thực hiện 4 lệnh sau để khôi phục toàn bộ hệ thống hoạt động đầy đủ:

### 1. Triển khai lại hạ tầng AWS (Terraform)
```powershell
cd d:\online-boutique\online-boutique-app\terraform-aws\environments\dev
terraform apply -auto-approve
```
*(Quá trình mất khoảng 10–12 phút để tạo mới VPC, EKS Spot Nodes, ElastiCache Redis).*

### 2. Cập nhật Kubeconfig
```powershell
aws eks update-kubeconfig --region ap-southeast-1 --name online-boutique-dev
```

### 3. Cài đặt lại ArgoCD
```powershell
cd d:\online-boutique\online-boutique-config
helm install argocd argo/argo-cd `
  --namespace argocd --create-namespace `
  -f argocd/install/values.yaml
```

### 4. Triển khai các ứng dụng (ArgoCD Applications)
```powershell
# Chờ pod ArgoCD sẵn sàng (~30s) rồi áp dụng:
kubectl apply -f argocd/apps/dev/aws-lb-controller.yaml
kubectl apply -f argocd/apps/dev/cluster-autoscaler.yaml
kubectl apply -f argocd/apps/dev/online-boutique.yaml
```

Ngay lập tức, ArgoCD sẽ tự động kéo các manifest từ repo `online-boutique-config`, kết nối với ElastiCache Redis và ứng dụng Online Boutique sẽ hoạt động bình thường trở lại.

---

## 5. Bảng Dự Toán Tiết Kiệm Chi Phí Khi Destroy Cuối Ngày

| Tài nguyên | Bật 24/7 (USD/tháng) | Bật 8h/ngày làm việc (USD/tháng) | Tiết kiệm (%) |
|------------|----------------------|-----------------------------------|---------------|
| EKS Control Plane ($0.10/h) | ~$73 | ~$24 | **~67%** |
| 3x EC2 t3.medium Spot | ~$30 | ~$10 | **~67%** |
| ElastiCache Redis Multi-AZ | ~$25 | ~$8 | **~68%** |
| NAT Gateway ($0.059/h) | ~$43 | ~$14 | **~67%** |
| Load Balancers | ~$25 | ~$8 | **~68%** |
| **Tổng cộng** | **~$196/tháng** | **~$64/tháng** | **Tiết kiệm ~$132/tháng (~67%)** |
