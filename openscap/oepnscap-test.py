#!/usr/bin/env python3
"""
OpenSCAP 보안 컴플라이언스 스캐너
OpenSCAP을 사용하여 시스템 보안 설정을 검사하는 도구

주의: OpenSCAP은 바이러스 검사 도구가 아닙니다!
- ClamAV: 바이러스/멀웨어 검사
- OpenSCAP: 보안 컴플라이언스 검사 (시스템 설정, 보안 정책 준수)
"""

import os
import sys
import subprocess
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
from pathlib import Path
import tempfile
import shutil

class OpenSCAPScanner:
    def __init__(self):
        self.oscap_path = shutil.which('oscap')
        self.results_dir = Path("openscap_results")
        self.results_dir.mkdir(exist_ok=True)
        
    def check_oscap_installation(self):
        """OpenSCAP 설치 확인"""
        if not self.oscap_path:
            print("❌ OpenSCAP이 설치되지 않았습니다.")
            print("설치 방법:")
            print("  Ubuntu/Debian: sudo apt-get install libopenscap8")
            print("  CentOS/RHEL: sudo yum install openscap-scanner")
            print("  macOS: brew install openscap")
            return False
        
        try:
            result = subprocess.run([self.oscap_path, '--version'], 
                                 capture_output=True, text=True)
            print(f"✅ OpenSCAP 설치됨: {result.stdout.strip()}")
            return True
        except Exception as e:
            print(f"❌ OpenSCAP 실행 오류: {e}")
            return False
    
    def download_security_content(self):
        """보안 컨텐츠 다운로드 (예: SCAP Security Guide)"""
        print("\n🔄 보안 컨텐츠 다운로드 중...")
        
        # SCAP Security Guide URL들
        content_urls = {
            "ubuntu": "https://github.com/ComplianceAsCode/content/releases/download/v0.1.68/scap-security-guide-0.1.68-ubuntu2004-ds.xml",
            "centos": "https://github.com/ComplianceAsCode/content/releases/download/v0.1.68/scap-security-guide-0.1.68-centos8-ds.xml",
            "rhel": "https://github.com/ComplianceAsCode/content/releases/download/v0.1.68/scap-security-guide-0.1.68-rhel8-ds.xml"
        }
        
        content_dir = Path("security_content")
        content_dir.mkdir(exist_ok=True)
        
        downloaded_files = []
        
        for os_name, url in content_urls.items():
            filename = f"{os_name}_security_guide.xml"
            filepath = content_dir / filename
            
            try:
                if not filepath.exists():
                    print(f"  다운로드 중: {os_name} 보안 가이드...")
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"  ✅ 다운로드 완료: {filename}")
                else:
                    print(f"  ✅ 이미 존재: {filename}")
                
                downloaded_files.append(filepath)
                
            except Exception as e:
                print(f"  ❌ {os_name} 다운로드 실패: {e}")
        
        return downloaded_files
    
    def list_profiles(self, datastream_file):
        """데이터스트림에서 사용 가능한 프로필 목록 조회"""
        try:
            cmd = [self.oscap_path, 'info', str(datastream_file)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"\n📋 {datastream_file.name}의 사용 가능한 프로필:")
                print(result.stdout)
                return result.stdout
            else:
                print(f"❌ 프로필 조회 실패: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ 프로필 조회 오류: {e}")
            return None
    
    def validate_datastream(self, datastream_file):
        """데이터스트림 파일 유효성 검사"""
        try:
            cmd = [self.oscap_path, 'ds', 'sds-validate', str(datastream_file)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {datastream_file.name} 유효성 검사 통과")
                return True
            else:
                print(f"❌ {datastream_file.name} 유효성 검사 실패:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ 유효성 검사 오류: {e}")
            return False
    
    def run_compliance_scan(self, datastream_file, profile_id=None):
        """컴플라이언스 스캔 실행"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"scan_results_{timestamp}.xml"
        report_file = self.results_dir / f"scan_report_{timestamp}.html"
        
        print(f"\n🔍 컴플라이언스 스캔 시작...")
        print(f"  대상 파일: {datastream_file.name}")
        if profile_id:
            print(f"  프로필: {profile_id}")
        
        try:
            # XCCDF 평가 실행
            cmd = [
                self.oscap_path, 'xccdf', 'eval',
                '--results', str(results_file)
            ]
            
            if profile_id:
                cmd.extend(['--profile', profile_id])
            
            cmd.append(str(datastream_file))
            
            print(f"  실행 명령: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 결과 분석
            if results_file.exists():
                print(f"✅ 스캔 완료! 결과 파일: {results_file}")
                
                # HTML 리포트 생성
                self.generate_html_report(results_file, report_file)
                
                # 결과 요약 출력
                self.parse_scan_results(results_file)
                
                return results_file, report_file
            else:
                print(f"❌ 스캔 실패: {result.stderr}")
                return None, None
                
        except Exception as e:
            print(f"❌ 스캔 오류: {e}")
            return None, None
    
    def generate_html_report(self, results_file, report_file):
        """XML 결과를 HTML 리포트로 변환"""
        try:
            cmd = [
                self.oscap_path, 'xccdf', 'generate', 'report',
                str(results_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                print(f"✅ HTML 리포트 생성: {report_file}")
            else:
                print(f"❌ HTML 리포트 생성 실패: {result.stderr}")
                
        except Exception as e:
            print(f"❌ HTML 리포트 생성 오류: {e}")
    
    def parse_scan_results(self, results_file):
        """스캔 결과 XML 파싱하여 요약 정보 출력"""
        try:
            tree = ET.parse(results_file)
            root = tree.getroot()
            
            # 네임스페이스 정의
            namespaces = {
                'xccdf': 'http://checklists.nist.gov/xccdf/1.2'
            }
            
            # 테스트 결과 통계
            test_results = root.find('.//xccdf:TestResult', namespaces)
            if test_results is not None:
                print("\n📊 스캔 결과 요약:")
                
                # 각 결과 타입별 카운트
                results_count = {
                    'pass': 0,
                    'fail': 0,
                    'error': 0,
                    'unknown': 0,
                    'notapplicable': 0,
                    'notselected': 0
                }
                
                rules = test_results.findall('.//xccdf:rule-result', namespaces)
                for rule in rules:
                    result_elem = rule.find('xccdf:result', namespaces)
                    if result_elem is not None:
                        result_type = result_elem.text
                        if result_type in results_count:
                            results_count[result_type] += 1
                
                # 결과 출력
                total_tests = sum(results_count.values())
                print(f"  전체 테스트: {total_tests}")
                print(f"  ✅ 통과: {results_count['pass']}")
                print(f"  ❌ 실패: {results_count['fail']}")
                print(f"  ⚠️  오류: {results_count['error']}")
                print(f"  ❓ 알 수 없음: {results_count['unknown']}")
                print(f"  🔷 해당 없음: {results_count['notapplicable']}")
                print(f"  ⭕ 선택 안함: {results_count['notselected']}")
                
                # 컴플라이언스 점수 계산
                if total_tests > 0:
                    compliance_score = (results_count['pass'] / (results_count['pass'] + results_count['fail'])) * 100
                    print(f"\n🎯 컴플라이언스 점수: {compliance_score:.1f}%")
            
        except Exception as e:
            print(f"❌ 결과 파싱 오류: {e}")
    
    def scan_file_permissions(self, target_path):
        """파일 권한 검사 (간단한 예시)"""
        print(f"\n🔍 파일 권한 검사: {target_path}")
        
        try:
            path = Path(target_path)
            if not path.exists():
                print(f"❌ 파일/디렉토리가 존재하지 않습니다: {target_path}")
                return False
            
            # 파일 권한 정보
            stat_info = path.stat()
            permissions = oct(stat_info.st_mode)[-3:]
            
            print(f"  권한: {permissions}")
            print(f"  소유자: {stat_info.st_uid}")
            print(f"  그룹: {stat_info.st_gid}")
            
            # 보안 권장사항 체크
            warnings = []
            
            # 월드 라이터블 체크
            if int(permissions[2]) & 2:  # 다른 사용자 쓰기 권한
                warnings.append("⚠️  다른 사용자가 쓰기 가능 (보안 위험)")
            
            # 실행 파일 권한 체크
            if path.is_file() and int(permissions[0]) & 1:  # 소유자 실행 권한
                if int(permissions[1]) & 1 or int(permissions[2]) & 1:  # 그룹/기타 실행 권한
                    warnings.append("⚠️  그룹/기타 사용자 실행 권한 (검토 필요)")
            
            if warnings:
                print("  보안 경고:")
                for warning in warnings:
                    print(f"    {warning}")
            else:
                print("  ✅ 권한 설정이 안전합니다")
            
            return True
            
        except Exception as e:
            print(f"❌ 권한 검사 오류: {e}")
            return False

def main():
    print("🔒 OpenSCAP 보안 컴플라이언스 스캐너")
    print("=" * 50)
    print("주의: OpenSCAP은 시스템 보안 설정을 검사하는 도구입니다.")
    print("바이러스 검사를 원한다면 ClamAV를 사용하세요!\n")
    
    scanner = OpenSCAPScanner()
    
    # OpenSCAP 설치 확인
    if not scanner.check_oscap_installation():
        print("\nOpenSCAP 설치 후 다시 실행해주세요.")
        return
    
    # 보안 컨텐츠 다운로드
    content_files = scanner.download_security_content()
    
    if not content_files:
        print("❌ 보안 컨텐츠를 다운로드할 수 없습니다.")
        return
    
    # 첫 번째 컨텐츠 파일로 테스트
    test_file = content_files[0]
    print(f"\n🎯 테스트 대상: {test_file.name}")
    
    # 데이터스트림 유효성 검사
    if not scanner.validate_datastream(test_file):
        print("❌ 데이터스트림 유효성 검사 실패")
        return
    
    # 사용 가능한 프로필 조회
    scanner.list_profiles(test_file)
    
    # 컴플라이언스 스캔 실행 (기본 프로필)
    results_file, report_file = scanner.run_compliance_scan(test_file)
    
    if results_file:
        print(f"\n📁 결과 파일:")
        print(f"  XML: {results_file}")
        if report_file and report_file.exists():
            print(f"  HTML: {report_file}")
    
    # 파일 권한 검사 예시
    test_paths = ["/etc/passwd", "/tmp", ".", __file__]
    for path in test_paths:
        scanner.scan_file_permissions(path)
    
    print(f"\n✅ OpenSCAP 테스트 완료!")
    print(f"📊 결과 디렉토리: {scanner.results_dir}")

if __name__ == "__main__":
    main()
