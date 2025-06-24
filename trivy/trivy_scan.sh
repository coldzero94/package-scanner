#!/bin/bash
set -e

echo "[+] Installing Trivy..."
apt-get update && apt-get install -y wget
wget https://github.com/aquasecurity/trivy/releases/latest/download/trivy_0.50.1_Linux-64bit.deb
dpkg -i trivy_0.50.1_Linux-64bit.deb

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
