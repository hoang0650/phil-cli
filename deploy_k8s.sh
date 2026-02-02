#!/bin/bash

# Dừng script nếu có lỗi
set -e

echo ">>> [1/4] Building Docker Image for Phil Agent..."
# Build image tên là 'phil-agent:latest' dùng chung cho Sandbox và Controller
docker build -t phil-agent:latest -f sandbox/Dockerfile .

# Nếu dùng K3s (như trên Runpod), cần import image vào K3s containerd
if command -v k3s &> /dev/null; then
    echo ">>> Importing image to K3s..."
    k3s ctr images import phil-agent.tar || echo "K3s image import skipped (using local docker)"
    # Lưu ý: Trên Runpod thường Docker và K8s dùng chung daemon hoặc cần cấu hình lại
fi

echo ">>> [2/4] Applying Namespaces & Storage..."
kubectl apply -f k8s/01-storage.yaml

echo ">>> [3/4] Deploying AI Brains (This may take a while)..."
# Bạn cần tạo file 02-brains.yaml chứa đầy đủ 5 model như hướng dẫn
kubectl apply -f k8s/02-brains.yaml

echo ">>> [4/4] Deploying Application Logic..."
kubectl apply -f k8s/03-app.yaml
kubectl apply -f k8s/04-ingress.yaml

echo ">>> DEPLOYMENT COMPLETE!"
echo "Check status using: kubectl get pods -n phil-ai"