#!/usr/bin/env python3
"""
OpenSCAP 간단 테스트 스크립트
- OpenSCAP 설치 확인
- 기본 파일 권한 검사
- 시스템 보안 설정 체크
"""

import os
import subprocess
import stat
from pathlib import Path

def check_openscap():
    """OpenSCAP 설치 확인"""
    print("🔍 OpenSCAP 설치 확인...")
    
    try:
        result = subprocess.run(['oscap', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ OpenSCAP 설치됨: {result.stdout.strip()}")
            return True
        else:
            print("❌ OpenSCAP이 설치되지 않았습니다.")
            return False
    except FileNotFoundError:
        print("❌ OpenSCAP이 설치되지 않았습니다.")
        print("설치 방법:")
        print("  macOS: brew install openscap")
        print("  Ubuntu: sudo apt-get install libopenscap8")
        return False

def check_file_permissions():
    """기본 파일 권한 검사"""
    print("\n🔍 파일 권한 검사...")
    
    # 검사할 파일/디렉토리 목록
    check_paths = [
        {"path": "/etc", "desc": "시스템 설정 디렉토리"},
        {"path": "/tmp", "desc": "임시 디렉토리"},
        {"path": Path.home(), "desc": "홈 디렉토리"},
        {"path": ".", "desc": "현재 디렉토리"}
    ]
    
    for item in check_paths:
        path = Path(item["path"])
        if not path.exists():
            print(f"❌ {item['desc']}: 경로 없음")
            continue
            
        try:
            # 권한 정보 가져오기
            file_stat = path.stat()
            mode = file_stat.st_mode
            
            # 권한을 8진수로 변환
            permissions = oct(mode)[-3:]
            
            # 보안 검사
            issues = []
            
            # 월드 라이터블 검사
            if mode & stat.S_IWOTH:
                issues.append("모든 사용자가 쓰기 가능")
            
            # 그룹 라이터블 검사 (민감한 디렉토리의 경우)
            if str(path) in ["/etc"] and mode & stat.S_IWGRP:
                issues.append("그룹이 쓰기 가능")
            
            if issues:
                print(f"⚠️  {item['desc']} ({permissions}): {', '.join(issues)}")
            else:
                print(f"✅ {item['desc']} ({permissions}): 안전")
                
        except Exception as e:
            print(f"❌ {item['desc']}: 검사 실패 - {e}")

def check_system_settings():
    """기본 시스템 보안 설정 검사"""
    print("\n🔍 시스템 보안 설정 검사...")
    
    checks = [
        {
            "name": "패스워드 파일 권한",
            "cmd": ["ls", "-l", "/etc/passwd"],
            "check": lambda output: "rw-r--r--" in output
        },
        {
            "name": "SSH 설정 파일",
            "cmd": ["ls", "-l", "/etc/ssh/sshd_config"],
            "check": lambda output: "rw-------" in output or "rw-r-----" in output
        }
    ]
    
    for check in checks:
        try:
            result = subprocess.run(check["cmd"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                if check["check"](result.stdout):
                    print(f"✅ {check['name']}: 안전")
                else:
                    print(f"⚠️  {check['name']}: 권한 검토 필요")
                    print(f"   {result.stdout.strip()}")
            else:
                print(f"❓ {check['name']}: 파일 없음 또는 접근 불가")
        except Exception as e:
            print(f"❌ {check['name']}: 검사 실패 - {e}")

def create_simple_oval_test():
    """간단한 OVAL 테스트 파일 생성"""
    print("\n🔍 간단한 OVAL 테스트 파일 생성...")
    
    oval_content = """<?xml version="1.0" encoding="UTF-8"?>
<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5" 
                   xmlns:unix-def="http://oval.mitre.org/XMLSchema/oval-definitions-5#unix"
                   xmlns:oval="http://oval.mitre.org/XMLSchema/oval-common-5">
  
  <generator>
    <oval:product_name>OpenSCAP Simple Test</oval:product_name>
    <oval:schema_version>5.11.1</oval:schema_version>
    <oval:timestamp>2024-01-01T00:00:00</oval:timestamp>
  </generator>
  
  <definitions>
    <definition class="compliance" id="oval:com.example:def:1" version="1">
      <metadata>
        <title>Check /tmp directory permissions</title>
        <description>Verify that /tmp directory has safe permissions</description>
      </metadata>
      <criteria>
        <criterion test_ref="oval:com.example:tst:1"/>
      </criteria>
    </definition>
  </definitions>
  
  <tests>
    <unix-def:file_test check="all" check_existence="all_exist" 
                        comment="Test /tmp permissions" id="oval:com.example:tst:1" version="1">
      <unix-def:object object_ref="oval:com.example:obj:1"/>
      <unix-def:state state_ref="oval:com.example:ste:1"/>
    </unix-def:file_test>
  </tests>
  
  <objects>
    <unix-def:file_object id="oval:com.example:obj:1" version="1">
      <unix-def:filepath>/tmp</unix-def:filepath>
    </unix-def:file_object>
  </objects>
  
  <states>
    <unix-def:file_state id="oval:com.example:ste:1" version="1">
      <unix-def:type>directory</unix-def:type>
      <unix-def:uwrite datatype="boolean">true</unix-def:uwrite>
      <unix-def:gwrite datatype="boolean">true</unix-def:gwrite>
      <unix-def:owrite datatype="boolean">false</unix-def:owrite>
    </unix-def:file_state>
  </states>
  
</oval_definitions>"""
    
    try:
        oval_file = Path("simple_test.oval.xml")
        with open(oval_file, 'w', encoding='utf-8') as f:
            f.write(oval_content)
        
        print(f"✅ OVAL 테스트 파일 생성: {oval_file}")
        
        # OVAL 파일 검증
        if check_openscap():
            try:
                result = subprocess.run(['oscap', 'oval', 'validate', str(oval_file)],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ OVAL 파일 유효성 검사 통과")
                    
                    # OVAL 평가 실행
                    result = subprocess.run(['oscap', 'oval', 'eval', 
                                           '--results', 'oval_results.xml',
                                           str(oval_file)],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print("✅ OVAL 평가 완료: oval_results.xml")
                    else:
                        print(f"⚠️  OVAL 평가 실패: {result.stderr}")
                else:
                    print(f"❌ OVAL 파일 유효성 검사 실패: {result.stderr}")
            except Exception as e:
                print(f"❌ OVAL 처리 오류: {e}")
        
        return oval_file
        
    except Exception as e:
        print(f"❌ OVAL 파일 생성 실패: {e}")
        return None

def main():
    print("🔒 OpenSCAP 간단 테스트")
    print("=" * 40)
    print("OpenSCAP은 시스템 보안 컴플라이언스 검사 도구입니다.")
    print("(바이러스 검사 도구가 아닙니다!)\n")
    
    # OpenSCAP 설치 확인
    openscap_available = check_openscap()
    
    # 기본 보안 검사
    check_file_permissions()
    check_system_settings()
    
    # OVAL 테스트 파일 생성 및 실행
    if openscap_available:
        oval_file = create_simple_oval_test()
        if oval_file:
            print(f"\n📁 생성된 파일: {oval_file}")
    
    print("\n✅ 간단 테스트 완료!")
    print("\n💡 OpenSCAP 주요 기능:")
    print("  - 시스템 보안 설정 검사")
    print("  - 컴플라이언스 정책 준수 확인")
    print("  - SCAP 표준 (OVAL, XCCDF, CPE) 지원")
    print("  - 보안 벤치마크 평가")

if __name__ == "__main__":
    main() 