# 🔍 Package Scanner

다양한 보안 스캐너 도구들을 통합한 종합 보안 검사 시스템입니다.

## 📖 프로젝트 개요

이 프로젝트는 서로 다른 보안 영역을 담당하는 **4가지 전문 스캐너**를 제공합니다:
- 🦠 **바이러스/멀웨어 검사** (ClamAV)
- 🐛 **컨테이너 취약점 검사** (Grype)
- 🔒 **시스템 보안 컴플라이언스** (OpenSCAP)
- 🛡️ **종합 보안 스캔** (Trivy)

각각은 **독립적인 목적**을 가지고 있어, 상황에 맞는 적절한 도구를 선택해서 사용할 수 있습니다.

---

## 🦠 ClamAV - 바이러스/멀웨어 스캐너

### 목적
- 파일과 디렉토리에서 **바이러스, 멀웨어, 악성코드** 검사
- 실시간 위협 탐지 및 격리

### 주요 기능
- ✅ 단일 파일 검사
- ✅ 디렉토리 재귀 검사  
- ✅ 대화형 모드 지원
- ✅ 상세한 검사 결과 리포트

### 사용법
```bash
cd clamav

# 기본 테스트
python clamav-test.py

# 고급 기능 (단일 파일)
python clamav-advanced.py file.txt

# 디렉토리 검사
python clamav-advanced.py -d /path/to/directory -r

# 대화형 모드
python clamav-advanced.py -i
```

### 설치 요구사항
```bash
# macOS
brew install clamav
brew services start clamav

# 의존성 설치
pip install -r requirements.txt
```

---

## 🐛 Grype - 컨테이너 취약점 스캐너

### 목적
- **Docker 이미지**의 알려진 취약점 검사
- **패키지 의존성**의 보안 취약점 분석
- DevSecOps 파이프라인에 통합 가능한 취약점 검사

### 주요 기능
- ✅ Docker 이미지 취약점 스캔
- ✅ 파일시스템 패키지 검사
- ✅ 심각도 필터링 (HIGH, CRITICAL)
- ✅ 다양한 출력 형식 지원

### 사용법
```bash
cd grype

# 셸 스크립트 실행
bash grype_scan.sh

# 수동 설치 후 사용
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
grype docker-archive:image.tar
```

### 언제 사용하나요?
- 🐳 Docker 이미지 배포 전 취약점 검사
- 📦 서드파티 패키지 의존성 보안 검토
- 🚀 CI/CD 파이프라인의 보안 게이트

---

## 🔒 OpenSCAP - 시스템 보안 컴플라이언스

### ⚠️ 중요: 이것은 바이러스 스캐너가 아닙니다!

### 목적
- **시스템 보안 설정**의 정책 준수 여부 검사
- **컴플라이언스 표준** (CIS, NIST, PCI DSS) 검증
- 보안 감사 및 규정 준수 확인

### 주요 기능
- ✅ 파일 권한 검사
- ✅ 시스템 설정 검증
- ✅ 보안 벤치마크 평가
- ✅ SCAP 표준 지원 (OVAL, XCCDF, CPE)

### 사용법
```bash
cd openscap

# 간단한 시스템 검사
python openscap-simple-test.py

# 전체 컴플라이언스 검사
python oepnscap-test.py
```

### 설치 요구사항
```bash
# macOS
brew install openscap

# Ubuntu
sudo apt-get install libopenscap8 openscap-utils

# 의존성 설치
pip install -r requirements.txt
```

### 언제 사용하나요?
- 🏢 기업 보안 정책 준수 확인
- 📋 정기 보안 감사
- 🛡️ 서버 보안 설정 검증
- 📊 컴플라이언스 리포트 생성

---

## 🛡️ Trivy - 종합 보안 스캐너

### 목적
- **All-in-One** 보안 스캐너
- 컨테이너, 파일시스템, Git 저장소 등 **다양한 타겟** 지원
- 취약점, 설정 오류, 시크릿 검사

### 주요 기능
- ✅ 컨테이너 이미지 취약점 스캔
- ✅ 파일시스템 보안 검사
- ✅ IaC (Infrastructure as Code) 검사
- ✅ 시크릿 키 탐지
- ✅ 라이센스 검사

### 사용법
```bash
cd trivy

# 셸 스크립트 실행
bash trivy_scan.sh

# 파이썬 스크립트 실행
python trivy_scan.py
```

### 언제 사용하나요?
- 🔍 종합적인 보안 검사가 필요할 때
- 🚀 CI/CD 파이프라인의 보안 스캔
- ☁️ 클라우드 인프라 보안 검증
- 🔐 코드 저장소의 시크릿 탐지

---

## 🎯 어떤 도구를 언제 사용할까요?

| 상황 | 추천 도구 | 이유 |
|------|----------|------|
| 💻 **개인 파일 바이러스 검사** | ClamAV | 전통적인 안티바이러스 기능 |
| 🐳 **Docker 이미지 배포 전** | Grype 또는 Trivy | 컨테이너 특화 취약점 검사 |
| 🏢 **기업 보안 감사** | OpenSCAP | 컴플라이언스 표준 준수 |
| 🚀 **CI/CD 보안 게이트** | Trivy | 종합적이고 빠른 스캔 |
| 📦 **의존성 취약점 검사** | Grype 또는 Trivy | 패키지 취약점 전문 |
| 🔒 **서버 보안 설정 검토** | OpenSCAP | 시스템 설정 전문 |

---

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd package-scanner
```

### 2. 각 도구별 의존성 설치
```bash
# ClamAV
cd clamav && pip install -r requirements.txt

# Grype  
cd ../grype && pip install -r requirements.txt

# OpenSCAP
cd ../openscap && pip install -r requirements.txt

# Trivy (별도 설치 스크립트 포함)
cd ../trivy
```

### 3. 테스트 실행
```bash
# 각 폴더에서 테스트 스크립트 실행
python clamav/clamav-test.py
python openscap/openscap-simple-test.py
bash grype/grype_scan.sh
bash trivy/trivy_scan.sh
```

---

## 🤔 왜 이런 도구들을 만들었나요?

### 보안의 다층 방어 (Defense in Depth)
현대의 보안은 **단일 도구로 해결할 수 없습니다**. 각각 다른 영역을 담당:

1. **ClamAV**: 파일 레벨 위협 (바이러스, 멀웨어)
2. **Grype**: 소프트웨어 공급망 보안 (취약한 패키지)
3. **OpenSCAP**: 시스템 설정 보안 (잘못된 권한, 설정)
4. **Trivy**: 종합 검사 (개발부터 운영까지)

### DevSecOps 통합
- 🔄 **개발 단계**: Trivy로 코드 및 의존성 검사
- 🏗️ **빌드 단계**: Grype로 컨테이너 이미지 검사  
- 🚀 **배포 단계**: OpenSCAP으로 인프라 컴플라이언스 검사
- 🔍 **운영 단계**: ClamAV로 실시간 위협 탐지

---

## 🛠️ 추가 정보

### 시스템 요구사항
- Python 3.11+
- Docker (컨테이너 스캔용)
- Linux/macOS (일부 도구는 Windows 미지원)

### 기여하기
1. Fork 저장소
2. 기능 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

### 라이센스
각 도구는 해당 프로젝트의 라이센스를 따릅니다.

---

**💡 팁**: 보안은 지속적인 과정입니다. 정기적으로 모든 도구를 사용해서 다각도로 시스템을 점검하세요!