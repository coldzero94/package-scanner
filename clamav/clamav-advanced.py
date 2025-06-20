import clamd
import sys
import os
import argparse
from pathlib import Path

def scan_file(file_path, verbose=False):
    """지정된 파일을 ClamAV로 검사하는 함수"""
    try:
        # clamd 데몬에 연결
        cd = clamd.ClamdUnixSocket()
        
        if verbose:
            print(f"ClamAV 상태: {cd.ping()}")
        
        # 파일 존재 여부 확인
        if not os.path.exists(file_path):
            print(f"❌ 파일이 존재하지 않습니다: {file_path}")
            return False, None
            
        # 파일 검사
        if verbose or True:  # 항상 검사 중임을 알림
            print(f"🔍 파일 검사 중: {file_path}")
        
        result = cd.scan(file_path)
        
        # 결과 처리
        if result:
            for file, (status, virus_name) in result.items():
                if status == 'FOUND':
                    print(f"⚠️  바이러스 발견: {virus_name}")
                    print(f"📁 파일: {file}")
                    return False, virus_name
                elif status == 'OK' or status == 'FOUND':
                    if verbose or status == 'OK':
                        print(f"✅ 파일이 안전합니다: {file}")
                    return True, None
        else:
            if verbose:
                print("✅ 검사 완료 - 문제없음")
            return True, None
            
    except clamd.ConnectionError:
        print("❌ ClamAV 데몬에 연결할 수 없습니다.")
        print("   설치: brew install clamav")
        print("   실행: brew services start clamav")
        return False, "CONNECTION_ERROR"
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False, str(e)

def scan_directory(dir_path, recursive=False, verbose=False):
    """디렉토리 내 파일들을 검사"""
    if not os.path.isdir(dir_path):
        print(f"❌ 디렉토리가 존재하지 않습니다: {dir_path}")
        return
    
    path = Path(dir_path)
    pattern = "**/*" if recursive else "*"
    
    total_files = 0
    infected_files = 0
    safe_files = 0
    
    print(f"📁 디렉토리 검사: {dir_path}")
    print(f"🔄 재귀 검사: {'예' if recursive else '아니오'}")
    print("=" * 50)
    
    for file_path in path.glob(pattern):
        if file_path.is_file():
            total_files += 1
            success, virus = scan_file(str(file_path), verbose=verbose)
            
            if success:
                safe_files += 1
            else:
                if virus and virus not in ["CONNECTION_ERROR"]:
                    infected_files += 1
    
    print("\n" + "=" * 50)
    print(f"📊 검사 결과 요약:")
    print(f"   전체 파일: {total_files}")
    print(f"   안전한 파일: {safe_files}")
    print(f"   감염된 파일: {infected_files}")

def main():
    parser = argparse.ArgumentParser(
        description="🦠 ClamAV 파일/디렉토리 검사 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python clamav-advanced.py file.txt                    # 단일 파일 검사
  python clamav-advanced.py -d /path/to/dir            # 디렉토리 검사
  python clamav-advanced.py -d /path/to/dir -r         # 재귀적 디렉토리 검사
  python clamav-advanced.py -i                         # 대화형 모드
        """
    )
    
    parser.add_argument('path', nargs='?', help='검사할 파일 또는 디렉토리 경로')
    parser.add_argument('-d', '--directory', action='store_true', 
                       help='디렉토리 검사 모드')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='디렉토리를 재귀적으로 검사')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='대화형 모드')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='상세한 출력')
    
    args = parser.parse_args()
    
    print("🦠 ClamAV 고급 파일 검사 도구")
    print("=" * 40)
    
    # 대화형 모드
    if args.interactive:
        while True:
            print("\n📋 옵션을 선택하세요:")
            print("1. 단일 파일 검사")
            print("2. 디렉토리 검사 (비재귀)")
            print("3. 디렉토리 검사 (재귀)")
            print("4. 종료")
            
            choice = input("선택 (1-4): ").strip()
            
            if choice == '4':
                print("👋 프로그램을 종료합니다.")
                break
            elif choice == '1':
                file_path = input("파일 경로: ").strip()
                if file_path:
                    scan_file(file_path, verbose=True)
            elif choice in ['2', '3']:
                dir_path = input("디렉토리 경로: ").strip()
                if dir_path:
                    scan_directory(dir_path, recursive=(choice=='3'), verbose=args.verbose)
            else:
                print("❌ 잘못된 선택입니다.")
    
    # 명령행 인자 처리
    elif args.path:
        if args.directory:
            scan_directory(args.path, recursive=args.recursive, verbose=args.verbose)
        else:
            scan_file(args.path, verbose=args.verbose)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 