# Description: 프로그램 실행 중 발생하는 이벤트 로그를 기록하는 스크립트

import logging
import datetime

# 로그 파일 관리 클래스
class Log:
    program_name = ''
    logger = ''
    formatter = ''
    file_name = ''
    file_handler = ''

    # 생성자 - 로그 파일 및 로거 설정
    def __init__(self, program_name):
        self.program_name = program_name
        self.file_name = '/home/ubuntu/project/logs/date/' + str(datetime.datetime.now().date()) + '.log'

        # 로거 설정
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 파일 핸들러 설정 및 로거에 추가
        self.file_handler = logging.FileHandler(self.file_name)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    # 소멸자 - 파일 핸들러 제거
    def __del__(self):
        self.logger.removeHandler(self.file_handler)

    # 로그 메시지 기록 함수
    def log(self, s):
        self.logger.info(s)
