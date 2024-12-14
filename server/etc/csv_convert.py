# Description: Upbit에서 수집한 OrderBook 및 체결 txt 데이터를 CSV 형식으로 변환하는 스크립트

import json
import csv
import os
from datetime import datetime, timedelta

# OrderBook txt 파일을 CSV로 변환하는 함수
def convert_orderbook_txt_to_csv(input_txt_file, output_csv_file):
    try:
        # 입력 파일에서 JSON 형식의 txt 데이터를 읽기
        with open(input_txt_file, 'r') as txt_file:
            lines = txt_file.readlines()

        # CSV 헤더 준비
        header = [
            'timestamp', 'total_ask_size', 'total_bid_size',
            'ask_price', 'bid_price', 'ask_size', 'bid_size'
        ]

        # 각 orderbook_unit에 대한 행 추출
        rows = []
        for line in lines:
            try:
                orderbook_data = json.loads(line.replace("'", '"'))  # 각 줄을 JSON 객체로 파싱 (싱글 쿼트를 더블 쿼트로 변환)
                # 필요한 필드만 추출 (불필요한 필드 제거)
                required_fields = ['timestamp', 'total_ask_size', 'total_bid_size', 'orderbook_units']
                orderbook_data = {key: orderbook_data[key] for key in required_fields if key in orderbook_data}

                # 각 orderbook_unit에 대해 데이터 추출
                for unit in orderbook_data.get('orderbook_units', []):
                    row = [
                        orderbook_data['timestamp'],
                        orderbook_data['total_ask_size'],
                        orderbook_data['total_bid_size'],
                        unit['ask_price'],
                        unit['bid_price'],
                        unit['ask_size'],
                        unit['bid_size']
                    ]
                    rows.append(row)
            except json.JSONDecodeError:
                # JSON 파싱 오류 시 로그 작성
                with open('/home/ubuntu/project/logs/crontab.log', 'a') as log_file:
                    log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - JSON decoding error in line: {line.strip()}\n")

        # 데이터를 CSV로 쓰기
        with open(output_csv_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            writer.writerows(rows)

        # 성공 로그 작성
        with open('/home/ubuntu/project/logs/crontab.log', 'a') as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Successfully converted {input_txt_file} to {output_csv_file}\n")

    except Exception as e:
        # 에러 로그 작성
        with open('/home/ubuntu/project/logs/crontab.log', 'a') as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error occurred while processing {input_txt_file}: {e}\n")

# 체결 txt 파일을 CSV로 변환하는 함수
def convert_tick_txt_to_csv(input_txt_file, output_csv_file):
    try:
        # 입력 파일에서 JSON 형식의 txt 데이터를 읽기
        with open(input_txt_file, 'r') as txt_file:
            lines = txt_file.readlines()

        # CSV 헤더 준비
        header = [
            'timestamp', 'trade_price', 'trade_volume', 'prev_closing_price', 'change_price', 'ask_bid'
        ]

        # 각 체결 데이터에 대한 행 추출
        rows = []
        for line in lines:
            try:
                tick_data = json.loads(line.replace("'", '"'))  # 각 줄을 JSON 객체로 파싱 (싱글 쿼트를 더블 쿼트로 변환)
                # 필요한 필드만 추출 (불필요한 필드 제거)
                required_fields = ['timestamp', 'trade_price', 'trade_volume', 'prev_closing_price', 'change_price', 'ask_bid']
                tick_data = {key: tick_data[key] for key in required_fields if key in tick_data}

                # 행 추가
                row = [
                    tick_data['timestamp'],
                    tick_data['trade_price'],
                    tick_data['trade_volume'],
                    tick_data['prev_closing_price'],
                    tick_data['change_price'],
                    tick_data['ask_bid']
                ]
                rows.append(row)
            except json.JSONDecodeError:
                # JSON 파싱 오류 시 로그 작성
                with open('/home/ubuntu/project/logs/crontab.log', 'a') as log_file:
                    log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - JSON decoding error in line: {line.strip()}\n")

        # 데이터를 CSV로 쓰기
        with open(output_csv_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            writer.writerows(rows)

        # 성공 로그 작성
        with open('/home/ubuntu/project/logs/crontab.log', 'a') as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Successfully converted {input_txt_file} to {output_csv_file}\n")

    except Exception as e:
        # 에러 로그 작성
        with open('/home/ubuntu/project/logs/crontab.log', 'a') as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error occurred while processing {input_txt_file}: {e}\n")

# 전날의 OrderBook 데이터를 CSV로 변환하는 함수
def convert_previous_day_orderbooks():
    base_dir = '/home/ubuntu/project/data/raw/orderbooks/'
    output_dir = '/home/ubuntu/project/data/csv/orderbooks/'
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

    # 출력 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # base_dir에 있는 파일들을 순회하며 전날 데이터만 처리
    for filename in os.listdir(base_dir):
        if filename.endswith('.txt') and filename.startswith(yesterday):
            input_txt_file = os.path.join(base_dir, filename)
            output_csv_file = os.path.join(output_dir, filename.replace('.txt', '.csv'))
            convert_orderbook_txt_to_csv(input_txt_file, output_csv_file)

# 전날의 체결 데이터를 CSV로 변환하는 함수
def convert_previous_day_ticks():
    base_dir = '/home/ubuntu/project/data/raw/ticks/'
    output_dir = '/home/ubuntu/project/data/csv/ticks/'
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

    # 출력 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # base_dir에 있는 파일들을 순회하며 전날 데이터만 처리
    for filename in os.listdir(base_dir):
        if filename.endswith('.txt') and filename.startswith(yesterday):
            input_txt_file = os.path.join(base_dir, filename)
            output_csv_file = os.path.join(output_dir, filename.replace('.txt', '.csv'))
            convert_tick_txt_to_csv(input_txt_file, output_csv_file)

# 실행: 전날 OrderBook 및 체결 데이터를 CSV로 변환
convert_previous_day_orderbooks()
convert_previous_day_ticks()
