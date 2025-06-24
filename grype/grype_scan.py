#!/usr/bin/env python3
"""
Grype 보안 스캐너 Python 스크립트
Docker 이미지의 취약점을 스캔하고 결과를 분석합니다.
"""

import subprocess
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# 로깅 설정
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
        
    def check_dependencies(self):
        """필요한 의존성들이 설치되어 있는지 확인"""
        dependencies = ['docker', 'curl']
        
        for dep in dependencies:
            try:
                subprocess.run(['which', dep], check=True, capture_output=True)
                logger.info(f"✓ {dep} 설치 확인됨")
            except subprocess.CalledProcessError:
                logger.error(f"✗ {dep}이 설치되지 않았습니다.")
                return False
        return True
        
    def install_grype(self):
        """Grype 설치"""
        try:
            logger.info("Grype 설치 중...")
            install_cmd = [
                'curl', '-sSfL', 
                'https://raw.githubusercontent.com/anchore/grype/main/install.sh'
            ]
            
            # curl로 설치 스크립트 다운로드 후 실행
            curl_process = subprocess.run(install_cmd, capture_output=True, text=True, check=True)
            
            # 스크립트 실행
            install_process = subprocess.run(
                ['sh', '-s', '--', '-b', '/usr/local/bin'],
                input=curl_process.stdout,
                text=True,
                check=True,
                capture_output=True
            )
            
            logger.info("Grype 설치 완료")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Grype 설치 실패: {e}")
            return False
            
    def check_grype_version(self):
        """Grype 버전 확인"""
        try:
            result = subprocess.run(['grype', 'version'], capture_output=True, text=True, check=True)
            logger.info(f"Grype 버전: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            logger.error("Grype가 설치되지 않았거나 실행할 수 없습니다.")
            return False
            
    def scan_image(self, image_name, output_file=None, format_type="json"):
        """Docker 이미지 스캔"""
        try:
            logger.info(f"이미지 스캔 시작: {image_name}")
            
            cmd = ['grype', f'docker:{image_name}', '-o', format_type]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # 결과 저장
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                logger.info(f"스캔 결과 저장됨: {output_file}")
            
            # JSON 결과 파싱
            if format_type == "json":
                scan_data = json.loads(result.stdout)
                return self.analyze_scan_results(scan_data, image_name)
            else:
                return result.stdout
                
        except subprocess.CalledProcessError as e:
            logger.error(f"이미지 스캔 실패 {image_name}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            return None
            
    def analyze_scan_results(self, scan_data, image_name):
        """스캔 결과 분석"""
        try:
            matches = scan_data.get('matches', [])
            total_vulnerabilities = len(matches)
            
            # 심각도별 분류
            severity_counts = {
                'Critical': 0,
                'High': 0,
                'Medium': 0,
                'Low': 0,
                'Negligible': 0,
                'Unknown': 0
            }
            
            for match in matches:
                vulnerability = match.get('vulnerability', {})
                severity = vulnerability.get('severity', 'Unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # 결과 요약
            summary = {
                'image': image_name,
                'timestamp': datetime.now().isoformat(),
                'total_vulnerabilities': total_vulnerabilities,
                'severity_breakdown': severity_counts,
                'scan_data': scan_data
            }
            
            # 요약 로그
            logger.info(f"=== {image_name} 스캔 결과 ===")
            logger.info(f"총 취약점 수: {total_vulnerabilities}")
            for severity, count in severity_counts.items():
                if count > 0:
                    logger.info(f"{severity}: {count}개")
                    
            return summary
            
        except Exception as e:
            logger.error(f"결과 분석 실패: {e}")
            return None
            
    def create_test_dockerfile(self):
        """테스트용 Dockerfile 생성"""
        dockerfile_content = """FROM python:3.11
RUN pip install flask requests
COPY . /app
WORKDIR /app
"""
        
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        logger.info("테스트용 Dockerfile 생성됨")
        
    def build_local_image(self, image_name="myapp:test"):
        """로컬 이미지 빌드"""
        try:
            logger.info(f"로컬 이미지 빌드 중: {image_name}")
            
            # Dockerfile이 없으면 생성
            if not os.path.exists('Dockerfile'):
                self.create_test_dockerfile()
                
            result = subprocess.run(
                ['docker', 'build', '-t', image_name, '.'],
                capture_output=True, text=True, check=True
            )
            
            logger.info(f"로컬 이미지 빌드 완료: {image_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"이미지 빌드 실패: {e}")
            return False
            
    def run_full_scan(self):
        """전체 스캔 프로세스 실행"""
        logger.info("=== Grype 보안 스캔 시작 ===")
        
        # 의존성 확인
        if not self.check_dependencies():
            logger.error("필요한 의존성이 설치되지 않았습니다.")
            return False
            
        # Grype 설치 (이미 설치되어 있으면 스킵)
        if not self.check_grype_version():
            if not self.install_grype():
                return False
            if not self.check_grype_version():
                return False
        
        # 결과 저장용 파일들
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        external_json = self.results_dir / f"external_scan_{timestamp}.json"
        local_json = self.results_dir / f"local_scan_{timestamp}.json"
        summary_file = self.results_dir / f"scan_summary_{timestamp}.json"
        
        results = {}
        
        # 1. 외부 이미지 스캔
        logger.info("=== 외부 이미지 스캔 (python:3.11) ===")
        external_result = self.scan_image("python:3.11", external_json)
        if external_result:
            results['external'] = external_result
            
        # 2. 로컬 이미지 빌드 및 스캔
        logger.info("=== 로컬 이미지 빌드 및 스캔 ===")
        if self.build_local_image():
            local_result = self.scan_image("myapp:test", local_json)
            if local_result:
                results['local'] = local_result
        
        # 3. 전체 결과 요약 저장
        if results:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"전체 결과 요약 저장됨: {summary_file}")
            
        # 4. 테이블 형태 결과도 생성
        self.generate_table_reports(timestamp)
        
        logger.info("=== 스캔 완료 ===")
        return True
        
    def generate_table_reports(self, timestamp):
        """테이블 형태의 보고서 생성"""
        try:
            # 외부 이미지 테이블 결과
            logger.info("테이블 형태 보고서 생성 중...")
            
            external_table = self.results_dir / f"external_scan_table_{timestamp}.txt"
            local_table = self.results_dir / f"local_scan_table_{timestamp}.txt"
            
            # 테이블 형태로 스캔
            self.scan_image("python:3.11", external_table, "table")
            self.scan_image("myapp:test", local_table, "table")
            
        except Exception as e:
            logger.error(f"테이블 보고서 생성 실패: {e}")

def main():
    """메인 실행 함수"""
    scanner = GrypeScanner()
    
    try:
        success = scanner.run_full_scan()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
        sys.exit(1)
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 