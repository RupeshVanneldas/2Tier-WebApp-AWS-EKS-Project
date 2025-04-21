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