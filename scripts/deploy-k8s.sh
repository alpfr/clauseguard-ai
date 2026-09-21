#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-713220200108}"
ECR_REPO_NAME="clauseguard-ai"
IMAGE_TAG="v3"
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}"

echo "============================================================"
echo "ClauseGuard AI - Kubernetes Production Deployment"
echo "Target ECR: ${IMAGE_URI}"
echo "============================================================"

# 1. ECR Login
echo "[1/5] Authenticating Docker with Amazon ECR..."
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# 2. Build multi-platform or linux/amd64 Docker image
echo "[2/5] Building Docker container (linux/amd64)..."
docker buildx build --platform linux/amd64 -t "${IMAGE_URI}" -t "${ECR_REPO_NAME}:${IMAGE_TAG}" --load .

# 3. Push to ECR
echo "[3/5] Pushing container image to Amazon ECR..."
docker push "${IMAGE_URI}"

# 4. Apply Kubernetes Manifests
echo "[4/5] Applying Kubernetes manifests..."
kubectl apply -f k8s/network-policy.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/ingress.yaml

# 5. Wait for rollout
echo "[5/5] Monitoring deployment rollout status..."
kubectl rollout status deployment/clauseguard-ai -n default --timeout=120s

echo ""
echo "✔ Deployment successful!"
echo "ClauseGuard AI is live at: https://clauseguard.alpfrtech.com"
