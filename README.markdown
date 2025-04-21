# Personal Project: Deployment of a 2-Tiered Web Application to Amazon EKS

## Introduction

This repository contains a personal project focused on containerization, Kubernetes, and cloud-native applications. The project enhances a 2-tiered web application (Flask frontend with MySQL backend), containerizes it, automates its build and deployment using GitHub Actions, and deploys it to a managed Kubernetes cluster on Amazon EKS. Key features include pod auto-scaling, persistent storage, and secure access to cloud resources.

## Project Objectives

- **Enhance the Web Application**: Add configurable background images, secure secrets management, and persistent storage.
- **Automate Build and Deployment**: Use GitHub Actions to streamline the CI/CD pipeline.
- **Deploy to Amazon EKS**: Ensure scalability, security, and resilience in a managed Kubernetes environment.

## Technologies and Services Used

- **Docker**: Containerization of the application.
- **GitHub Actions**: Automation of build, test, and deployment.
- **Amazon ECR**: Secure storage of Docker images.
- **Amazon EKS**: Managed Kubernetes cluster hosting.
- **Amazon S3**: Storage for background images.
- **Amazon EBS**: Persistent storage for MySQL.
- **AWS IAM**: Identity and access management.
- **kubectl**: Kubernetes cluster management.
- **eksctl**: EKS cluster creation.

## Project Overview

### 1. Enhancing the Web Application

- **Background Image**: Replaced solid background with an image from a private S3 bucket, configured via a Kubernetes ConfigMap.
- **Secrets Management**: MySQL credentials and AWS credentials for S3 access are passed as Kubernetes Secrets.
- **Logging**: Added log entries for the background image URL.
- **Header Customization**: Included a custom name and slogan in the HTML header via ConfigMap environment variables.
- **Port Configuration**: Flask application listens on port 81.

### 2. Containerization and Local Testing

- **Dockerfile**: Built a Docker image using a Python base, installed dependencies, and configured to run on port 81.
- **Local Testing**: Tested the image in Cloud9 to verify functionality before deployment.

### 3. Automating Build and Deployment

- **GitHub Actions**: Workflow triggers on main branch commits, builds the Docker image, runs tests, and pushes to Amazon ECR.
- **Authentication**: Uses GitHub Secrets for AWS credentials to access ECR.

### 4. Deploying to Amazon EKS

- **Cluster Setup**: Created an EKS cluster with 2 worker nodes and a "final" namespace using `eksctl`.
- **Kubernetes Manifests**:
  - **ConfigMap**: Supplies background image URL.
  - **Secrets**: Manages MySQL credentials, AWS credentials, and ECR image pull secrets.
  - **PersistentVolumeClaim**: 2Gi storage with ReadWriteOnce access for MySQL.
  - **ServiceAccount**: "rvServiceAccount" with a Role and RoleBinding for namespace permissions.
  - **Deployments**: MySQL (1 replica) with PVC and Flask (1 replica) from ECR.
  - **Services**: Exposes MySQL internally and Flask to the internet.

### 5. Verifying Functionality

- **Browser Access**: Confirmed Flask app loads with the correct background image.
- **Persistence**: Verified data persists after MySQL pod deletion/recreation.
- **Dynamic Updates**: Updated S3 image and ConfigMap, confirmed changes in the browser.

## Setup and Deployment Instructions

### Prerequisites

- AWS account with EKS, ECR, S3, and IAM permissions.
- GitHub account and repository.
- Docker, `kubectl`, and `eksctl` installed locally.

### Deployment Commands

Below are the commands used to set up and deploy the project:

```bash
# Configure AWS credentials
vi ~/.aws/credentials  # Add AWS credentials
cat ~/.aws/credentials  # Verify credentials

# Install dependencies
sudo yum -y install jq gettext bash-completion

# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv -v /tmp/eksctl /usr/local/bin

# Install kubectl
curl -LO https://dl.k8s.io/release/v1.29.13/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/
alias k=kubectl
k version --client

# Create EKS cluster
eksctl create cluster -f eks_config.yaml
k get nodes

# Create namespace
k create ns final

# Deploy AWS EBS CSI driver
k apply -k 'github.com/kubernetes-sigs/aws-ebs-csi-driver/deploy/kubernetes/overlays/stable/?ref=release-1.32'

# Apply service account, role, and role binding
k apply -f ./service-account/sa.yaml
k apply -f ./service-account/role.yaml
k apply -f ./service-account/role-binding.yaml

# Verify namespace access
kubectl get namespaces --as=system:serviceaccount:final:rvServiceAccount
k describe clusterroles rv-ns-admin

# Deploy MySQL resources
k apply -f ./mysql-db/secrets.yaml
k apply -f ./mysql-db/pvc.yaml
k apply -f ./mysql-db/headless.yaml
k apply -f ./mysql-db/deployment.yaml

# Deploy Flask application resources
k apply -f ./web-app/secrets.yaml
k apply -f ./web-app/configMap.yaml
k apply -f ./web-app/service.yaml
k apply -f ./web-app/deployment.yaml

# Verify pods
k get pods -n final

# Test PVC by deleting MySQL pod
k delete pod mysql-0 -n final

# Restart Flask deployment to reconnect with new DB pod
kubectl rollout restart deployment application -n final

# Update background image URL in ConfigMap
k apply -f ./web-app/configMap.yaml
kubectl rollout restart deployment application -n final

# Cleanup
k delete ns final
eksctl delete cluster --name rv-eks-cluster --region us-east-1
```

### Steps

1. **Clone the Repository**.

2. **Configure ECR**: Create an ECR repository.

3. **Set GitHub Secrets**: Add `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION`.

4. **Automate Build**: Push to main branch to trigger GitHub Actions.

5. **Create EKS Cluster**: Use the `eksctl` command above with your `eks_config.yaml`.

6. **Deploy Manifests**: Apply Kubernetes manifests as shown in the commands.

7. **Verify the pods locally**: Check services and pods using `kubectl get` commands.

8. **Verify the application**: Copy & paste the DNS of LoadBalancer (don't forget to add "http://").

## Conclusion

This project demonstrates a fully automated, scalable, and secure cloud-native application deployment, showcasing expertise in containerization and Kubernetes orchestration.