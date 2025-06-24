#!/bin/bash
set -e

# Grype 설치
echo "[+] Installing Grype..."
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Grype 버전 확인
grype version

# /image 디렉토리에 있는 tar 파일 스캔
echo "[+] Scanning local tar image: /image/python_3.11.tar"
grype tar:/image/python_3.11.tar -o table > scan_external.txt

# 결과 출력
echo -e "\n=== Scan Result ==="
cat scan_external.txt
