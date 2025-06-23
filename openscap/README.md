# OpenSCAP 보안 컴플라이언스 스캐너

## ⚠️ 중요한 차이점

**OpenSCAP ≠ 바이러스 스캐너**

- **ClamAV**: 바이러스/멀웨어 검사 도구
- **OpenSCAP**: 보안 컴플라이언스 검사 도구 (시스템 설정, 보안 정책)

## OpenSCAP이란?

OpenSCAP은 **Security Content Automation Protocol (SCAP)** 표준을 구현한 도구로, 시스템의 보안 설정이 정책에 맞는지 검사합니다.

### 주요 기능

✅ **시스템 보안 설정 검사**
- 파일 권한 검사
- 사용자 계정 정책
- 네트워크 설정
- 서비스 구성

✅ **컴플라이언스 검사**
- CIS 벤치마크
- NIST 800-53
- PCI DSS
- HIPAA

✅ **표준 지원**
- OVAL (Open Vulnerability Assessment Language)
- XCCDF (eXtensible Configuration Checklist Description Format)
- CPE (Common Platform Enumeration)

## 설치 방법

### macOS
```bash
brew install openscap
```

### Ubuntu/Debian
```bash
sudo apt-get install libopenscap8 openscap-utils
```

### CentOS/RHEL
```bash
sudo yum install openscap-scanner scap-security-guide
```

## 사용법

### 1. 간단한 테스트 실행
```bash
python3 openscap-simple-test.py
```

### 2. 전체 테스트 실행
```bash
python3 oepnscap-test.py
```

### 3. 직접 OpenSCAP 명령 사용

#### OVAL 평가
```bash
oscap oval eval --results results.xml definition.oval.xml
```

#### XCCDF 평가
```bash
oscap xccdf eval --profile xccdf_profile --results results.xml datastream.xml
```

#### 보고서 생성
```bash
oscap xccdf generate report results.xml > report.html
```

## 파일 구조

```
openscap/
├── oepnscap-test.py          # 메인 테스트 스크립트
├── openscap-simple-test.py   # 간단한 테스트 스크립트
├── requirements.txt          # Python 의존성
└── README.md                # 이 파일
```

## 테스트 결과 예시

### 컴플라이언스 스캔 결과
```
📊 스캔 결과 요약:
  전체 테스트: 245
  ✅ 통과: 189
  ❌ 실패: 32
  ⚠️  오류: 3
  ❓ 알 수 없음: 5
  🔷 해당 없음: 16

🎯 컴플라이언스 점수: 85.5%
```

### 파일 권한 검사 결과
```
🔍 파일 권한 검사: /etc/passwd
  권한: 644
  소유자: 0
  그룹: 0
  ✅ 권한 설정이 안전합니다
```

## 보안 컨텐츠 소스

- [SCAP Security Guide](https://github.com/ComplianceAsCode/content)
- [NIST National Checklist Program](https://nvd.nist.gov/ncp/repository)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)

## 활용 사례

### 1. 서버 보안 감사
```bash
# Ubuntu 서버 CIS 벤치마크 검사
oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_cis \
  --results server-audit.xml ubuntu-cis-ds.xml
```

### 2. 정기 컴플라이언스 체크
```bash
# 주간 보안 체크 (cron 작업)
0 2 * * 1 /usr/bin/oscap xccdf eval --profile baseline --results weekly-scan.xml
```

### 3. 개발 환경 보안 검증
```bash
# 개발 서버 기본 보안 설정 검사
python3 openscap-simple-test.py
```

## 참고 자료

- [OpenSCAP 공식 사이트](https://www.open-scap.org/)
- [OpenSCAP GitHub](https://github.com/OpenSCAP/openscap)
- [SCAP 표준 문서](https://csrc.nist.gov/projects/security-content-automation-protocol)
- [OpenSCAP 사용자 매뉴얼](https://static.open-scap.org/openscap-1.3/oscap_user_manual.html)

## 문제 해결

### OpenSCAP 설치 문제
```bash
# macOS에서 Homebrew로 설치
brew install openscap

# 의존성 패키지 설치
brew install libxml2 libxslt
```

### 권한 오류
```bash
# 관리자 권한으로 실행
sudo python3 oepnscap-test.py
```

### 컨텐츠 다운로드 실패
- 네트워크 연결 확인
- 방화벽 설정 확인
- 프록시 설정 확인

---

**💡 팁**: OpenSCAP은 시스템 관리자와 보안 담당자를 위한 도구입니다. 개인 사용자라면 기본적인 파일 권한 검사 정도만 활용하세요! 