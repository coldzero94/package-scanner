#!/bin/bash
set -e

# Grype 설치
echo "[+] Installing Grype..."
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Grype 버전 확인
grype version

# 외부 이미지 스캔 (예: python:3.11)
echo "[+] Scanning external image: python:3.11"
grype docker:python:3.11 -o table > scan_external.txt

# 내부 빌드 이미지 생성
echo "[+] Building local image: myapp:test"
echo -e "FROM python:3.11\nRUN pip install flask" > Dockerfile
docker build -t myapp:test .

# 내부 이미지 스캔
echo "[+] Scanning local image: myapp:test"
grype docker:myapp:test -o table > scan_local.txt

# 결과 확인
echo -e "\n=== External Image Scan Result ==="
cat scan_external.txt
echo -e "\n=== Local Image Scan Result ==="
cat scan_local.txt
