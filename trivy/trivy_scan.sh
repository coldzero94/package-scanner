#!/bin/bash
set -e

echo "[+] Installing Trivy..."
apt-get update && apt-get install -y wget curl

# 공식 install.sh 사용 (버전 명시 가능)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | bash -s -- -b /usr/local/bin

echo "[+] Checking Trivy version..."
trivy --version

echo "[+] Scanning Docker image: python:3.11"
trivy image --severity HIGH,CRITICAL --format table -o result_image.txt python:3.11

echo "[+] Scanning filesystem: ./my_app"
mkdir -p my_app
echo "print('test')" > my_app/test.py
trivy fs --severity HIGH,CRITICAL --format table -o result_fs.txt ./my_app

echo -e "\n=== Docker Image Scan ==="
cat result_image.txt
echo -e "\n=== Filesystem Scan ==="
cat result_fs.txt
