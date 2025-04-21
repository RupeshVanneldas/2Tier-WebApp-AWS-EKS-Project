**⚙️ 2-Tier Web App Deployment to Amazon EKS**  
[![License](https://img.shields.io/badge/License-GNU-blue.svg)](LICENSE) [![EKS](https://img.shields.io/badge/Amazon%20EKS-⁠v1.29.13-0099ff)](https://aws.amazon.com/eks/) [![Docker](https://img.shields.io/badge/Docker-Certified-blue.svg)](https://www.docker.com/)  

---  

## 📋 Table of Contents
1. [🚀 Project Overview](#%EF%B8%8F-project-overview)
2. [🎯 Objectives](#-objectives)
3. [🛠️ Tech Stack](#️-tech-stack)
4. [⚙️ Architecture Diagram](#️-architecture-diagram)
5. [📦 Installation & Deployment](#-installation--deployment)
   - [Prerequisites](#prerequisites)
   - [Setup](#setup)
   - [Kubernetes Manifests](#kubernetes-manifests)
6. [✅ Verification](#-verification)
7. [🔧 CI/CD Pipeline](#-ci_cd-pipeline)
8. [📈 Features](#-features)
9. [🤝 Contributing](#-contributing)
10. [✉️ Contact & License](#️-contact--license)

---

## 🚀 Project Overview
> A **2-Tier Web Application** with a Flask frontend and MySQL backend, fully containerized and deployed on **Amazon EKS**. Includes auto-scaling, persistent storage, and secure secret management.  

![EKS Architecture](docs/eks-architecture.png)  
*Figure: High-level architecture diagram*  

---

## 🎯 Objectives
- 🎨 **UI Enhancements**: Configurable background image via S3 and ConfigMap
- 🔐 **Secrets Management**: Kubernetes Secrets for DB & AWS credentials
- 💾 **Persistence**: AWS EBS CSI driver for durable MySQL storage
- 🔄 **CI/CD**: Automated build, test, and deploy with GitHub Actions
- ⚖️ **Scalability**: Horizontal Pod Autoscaler for the Flask app

---

## 🛠️ Tech Stack
| Layer             | Technology                           |
|-------------------|--------------------------------------|
| **Container**     | Docker                               |
| **CI/CD**         | GitHub Actions                       |
| **Registry**      | Amazon ECR                           |
| **Orchestration** | Amazon EKS (Kubernetes v1.29.13)     |
| **Storage**       | Amazon S3 (images), Amazon EBS (PVC) |
| **IAM**           | AWS IAM Roles & ServiceAccounts      |
| **CLI Tools**     | kubectl, eksctl, awscli, jq         |

---

## ⚙️ Architecture Diagram
![image](https://github.com/user-attachments/assets/d6e73599-00db-4408-89d8-b182c4019fd0)

---

## 📦 Installation & Deployment

### Prerequisites
- AWS Account with EKS, ECR, S3, IAM permissions
- GitHub Repository
- Local tools: `docker`, `kubectl`, `eksctl`, `awscli`, `jq`

### Setup
```bash
# 1. Configure AWS CLI
aws configure

# 2. Install eksctl & kubectl
curl -sSL https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz | tar xz -C /usr/local/bin
curl -LO https://dl.k8s.io/release/v1.29.13/bin/linux/amd64/kubectl && chmod +x kubectl && mv kubectl /usr/local/bin

eksctl version && kubectl version --client
```

### Create EKS Cluster
```bash
eksctl create cluster -f eks_config.yaml --region us-east-1
kubectl get nodes
```

### Kubernetes Manifests
1. **Namespace & CSI Driver**
   ```bash
   kubectl create ns final
   kubectl apply -k "github.com/kubernetes-sigs/aws-ebs-csi-driver/deploy/kubernetes/overlays/stable/?ref=release-1.32"
   ```
2. **RBAC**
   ```bash
   kubectl apply -f service-account/sa.yaml
   kubectl apply -f service-account/role.yaml
   kubectl apply -f service-account/role-binding.yaml
   ```
3. **MySQL Deployment**
   ```bash
   kubectl apply -f mysql-db/secrets.yaml
   kubectl apply -f mysql-db/pvc.yaml
   kubectl apply -f mysql-db/headless.yaml
   kubectl apply -f mysql-db/deployment.yaml
   ```
4. **Flask App Deployment**
   ```bash
   kubectl apply -f web-app/secrets.yaml
   kubectl apply -f web-app/configMap.yaml
   kubectl apply -f web-app/service.yaml
   kubectl apply -f web-app/deployment.yaml
   ```

---

## ✅ Verification
1. **Access App**: Obtain LoadBalancer DNS (`kubectl get svc -n final`) and open in browser.
2. **Persistence Test**:
   ```bash
   kubectl delete pod mysql-0 -n final
   kubectl rollout restart deployment web-app -n final
   ```
   Data persists after pod recreation.
3. **ConfigMap Update**: Change S3 URL, reapply, and restart deployment to see new background.

---

## 🔧 CI/CD Pipeline
![CI Pipeline](docs/github-actions.png)
1. Push to `main` → triggers GitHub Actions
2. Build & test Docker image
3. Push to ECR
4. Apply k8s manifests to EKS via `kubectl` (GitHub OIDC)

---

## 📈 Features
- **Auto-Scaling**: HPA configured for Flask deployment
- **Logging**: Background image URL & app logs
- **Monitoring**: [Prometheus & Grafana](#) (future)
- **Configurable**: Environment via ConfigMap & Secrets

---

## 🤝 Contributing
1. Fork repo
2. Create feature branch
3. Submit PR with issue reference
4. CI will run tests & lint checks

---

## ✉️ Contact & License
- **Author**: Rupesh Vanneldas
- **Email**: rupeshvanneldas27@gmail.com

Licensed under the [GNU License](LICENSE).

