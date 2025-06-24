import subprocess
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('grype_scan.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class GrypeScanner:
    def __init__(self):
        self.results_dir = Path("scan_results")
        self.results_dir.mkdir(exist_ok=True)

    def install_grype(self):
        try:
            logger.info("Installing Grype...")
            subprocess.run([
                "wget", "-qO-", 
                "https://raw.githubusercontent.com/anchore/grype/main/install.sh"
            ], check=True, stdout=subprocess.PIPE)

            subprocess.run(
                "wget -qO- https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin",
                shell=True, check=True
            )
            logger.info("Grype installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Grype installation failed: {e}")
            return False

    def scan_image(self, image_name, output_file="scan_output.json"):
        try:
            logger.info(f"Scanning image: {image_name}")
            subprocess.run(["docker", "pull", image_name], check=True)
            result = subprocess.run(
                ["grype", f"docker:{image_name}", "-o", "json"],
                capture_output=True, text=True, check=True
            )
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            logger.info(f"Scan results saved to: {output_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Scan failed: {e}")

def main():
    scanner = GrypeScanner()
    if scanner.install_grype():
        scanner.scan_image("python:3.11")

if __name__ == "__main__":
    main()
