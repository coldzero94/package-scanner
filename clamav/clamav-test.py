import clamd
import sys
import os

def scan_file(file_path):
    """지정된 파일을 ClamAV로 검사하는 함수"""
    try:
        # clamd 데몬에 연결
        cd = clamd.ClamdUnixSocket()  # 또는 clamd.ClamdNetworkSocket("127.0.0.1", 3310)
        
        # 연결 테스트
        print(f"ClamAV 상태: {cd.ping()}")
        
        # 파일 존재 여부 확인
        if not os.path.exists(file_path):
            print(f"❌ 파일이 존재하지 않습니다: {file_path}")
            return False
            
        # 파일 검사
        print(f"🔍 파일 검사 중: {file_path}")
        result = cd.scan(file_path)
        
        # 결과 출력
        if result:
            for file, (status, virus_name) in result.items():
                if status == 'FOUND':
                    print(f"⚠️  바이러스 발견: {virus_name}")
                    print(f"📁 파일: {file}")
                elif status == 'OK':
                    print(f"✅ 파일이 안전합니다: {file}")
        else:
            print("✅ 검사 완료 - 문제없음")
            
        return True
        
    except clamd.ConnectionError:
        print("❌ ClamAV 데몬에 연결할 수 없습니다.")
        print("   - ClamAV가 설치되어 있는지 확인하세요: brew install clamav")
        print("   - 데몬이 실행 중인지 확인하세요: brew services start clamav")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def main():
    """메인 함수"""
    print("🦠 ClamAV 파일 검사 도구")
    print("=" * 40)
    
    # 방법 1: 명령행 인자로 받기
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"📝 명령행에서 받은 경로: {file_path}")
        scan_file(file_path)
    else:
        # 방법 2: 실행 중에 입력받기
        while True:
            file_path = input("\n📁 검사할 파일 경로를 입력하세요 (종료: 'quit' 또는 'q'): ").strip()
            
            if file_path.lower() in ['quit', 'q', 'exit']:
                print("👋 프로그램을 종료합니다.")
                break
                
            if not file_path:
                print("❌ 파일 경로를 입력해주세요.")
                continue
                
            # 상대 경로를 절대 경로로 변환
            file_path = os.path.abspath(file_path)
            
            scan_file(file_path)
            
            # 계속 검사할지 물어보기
            continue_scan = input("\n다른 파일을 검사하시겠습니까? (y/n): ").strip().lower()
            if continue_scan not in ['y', 'yes', '']:
                print("👋 프로그램을 종료합니다.")
                break

if __name__ == "__main__":
    main()
