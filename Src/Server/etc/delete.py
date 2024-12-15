# Description: EC2 EBS의 최적화를 위해 지정된 디렉토리에서 오래된 파일들을 삭제하는 스크립트

import os
import logging

# 로그 파일 설정
log_file = "/home/ubuntu/project/logs/crontab.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

# 파일 관리할 디렉토리 설정
orderbooks_dir = "/home/ubuntu/project/data/raw/orderbooks/"
ticks_dir = "/home/ubuntu/project/data/raw/ticks/"
csv_orderbooks_dir = "/home/ubuntu/project/data/csv/orderbooks/"
csv_ticks_dir = "/home/ubuntu/project/data/csv/ticks/"

# 최대 파일 수 설정
max_files = 5

# 지정된 디렉토리에서 오래된 파일들을 삭제하는 함수
def remove_old_files(directory, max_files):
    # 디렉토리 내의 모든 파일 경로 목록 생성
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # 파일 수가 최대 파일 수를 초과할 경우 오래된 파일 삭제
    if len(files) > max_files:
        files.sort(key=lambda x: os.path.getmtime(x))  # 수정 시간 기준으로 정렬
        for file in files[:len(files) - max_files]:
            os.remove(file)  # 파일 삭제
            logging.info(f"Deleted file: {file}")  # 로그 작성

# 각 디렉토리에서 오래된 파일을 관리하는 함수
def manage_files():
    remove_old_files(orderbooks_dir, max_files)
    remove_old_files(ticks_dir, max_files)
    remove_old_files(csv_orderbooks_dir, max_files)
    remove_old_files(csv_ticks_dir, max_files)

# 실행
if __name__ == "__main__":
    manage_files()
