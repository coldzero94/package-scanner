import subprocess
import os

def install_trivy():
    subprocess.run([
        "bash", "-c",
        "apt-get update && apt-get install -y wget && "
        "wget https://github.com/aquasecurity/trivy/releases/latest/download/trivy_0.50.1_Linux-64bit.deb && "
        "dpkg -i trivy_0.50.1_Linux-64bit.deb"
    ], check=True)

def scan_image(image):
    subprocess.run(["trivy", "image", "--severity", "HIGH,CRITICAL", image], check=True)

def scan_fs(path):
    subprocess.run(["trivy", "fs", "--severity", "HIGH,CRITICAL", path], check=True)

if __name__ == "__main__":
    print("[+] Installing Trivy...")
    install_trivy()

    print("[+] Scanning image...")
    scan_image("python:3.11")

    print("[+] Scanning directory...")
    os.makedirs("my_app", exist_ok=True)
    with open("my_app/test.py", "w") as f:
        f.write("print('hello')")
    scan_fs("my_app")
