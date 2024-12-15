# Description: Upbit에서 수집된 어제의 호가창과 체결 데이터를 S3 버킷에 비동기적으로 업로드하는 스크립트

import os
import logging
import boto3
from datetime import datetime, timedelta
import asyncio
import aiofiles
import aiobotocore.session

# 로그 파일 경로 설정
log_file = "/home/ubuntu/project/logs/crontab.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

# 기존 Orderbooks와 Ticks 파일들이 있는 디렉토리 경로
orderbooks_dir = "/home/ubuntu/project/data/raw/orderbooks/"
ticks_dir = "/home/ubuntu/project/data/raw/ticks/"
# CSV 내의 Orderbooks와 Ticks 파일들이 있는 디렉토리 경로
csv_orderbooks_dir = "/home/ubuntu/project/data/csv/orderbooks/"
csv_ticks_dir = "/home/ubuntu/project/data/csv/ticks/"

# S3 버킷 이름 및 리전 설정
bucket_name = "observator-s3"
s3_region = "ap-northeast-2"

# 세션 생성
session = boto3.session.Session()
s3_client = session.client(
    "s3",
    region_name=s3_region,
)

# S3에 파일을 업로드하는 비동기 함수
async def upload_to_s3(file_name, s3_file_name):
    session = aiobotocore.session.get_session()
    async with session.create_client(
        "s3",
        region_name=s3_region,
    ) as client:
        try:
            # 파일이 이미 S3에 존재하는지 확인
            try:
                await client.head_object(Bucket=bucket_name, Key=s3_file_name)
                logging.info(f"File {s3_file_name} already exists in S3, skipping upload.")
                return
            except client.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    pass  # 파일이 존재하지 않으면 업로드 계속 진행
                else:
                    raise
            # 파일을 비동기로 열고 데이터를 읽어 S3에 업로드
            async with aiofiles.open(file_name, 'rb') as f:
                data = await f.read()
                await client.put_object(Bucket=bucket_name, Key=s3_file_name, Body=data)
            logging.info(f"Successfully uploaded {file_name} to S3 as {s3_file_name}")
        except Exception as e:
            logging.error(f"Error occurred while uploading {file_name} to S3: {str(e)}")

# 어제 날짜의 데이터를 지정
def is_yesterday(file_name):
    try:
        file_date_str = file_name.split('.')[0][-8:]
        file_date = datetime.strptime(file_date_str, "%Y%m%d").date()
        yesterday = (datetime.now() - timedelta(days=1)).date()
        return file_date == yesterday
    except Exception as e:
        logging.error(f"Error occurred while parsing date from file name {file_name}: {str(e)}")
        return False

# Orderbooks와 Ticks 파일들을 S3에 업로드하는 비동기 함수
async def upload_orderbooks_and_ticks():
    # 기존 Orderbooks 파일 목록 검색 (어제 날짜의 데이터만)
    orderbooks_files = [f for f in os.listdir(orderbooks_dir) if f.endswith('.txt') and is_yesterday(f)]
    ticks_files = [f for f in os.listdir(ticks_dir) if f.endswith('.txt') and is_yesterday(f)]
    tasks = []
    
    for orderbook_file in orderbooks_files:
        file_path = os.path.join(orderbooks_dir, orderbook_file)
        s3_file_name = f"raw/orderbooks/{orderbook_file}"
        tasks.append(upload_to_s3(file_path, s3_file_name))
    
    for tick_file in ticks_files:
        file_path = os.path.join(ticks_dir, tick_file)
        s3_file_name = f"raw/ticks/{tick_file}"
        tasks.append(upload_to_s3(file_path, s3_file_name))

    # 기존 Orderbooks와 Ticks 파일이 있을 경우 업로드 작업 실행
    if tasks:
        await asyncio.gather(*tasks)
    else:
        logging.info("No raw Orderbooks or Ticks files found to upload for yesterday.")

# CSV 내 Orderbooks와 Ticks 파일들을 S3에 업로드하는 비동기 함수
async def upload_csv_orderbooks_and_ticks():
    # CSV 내 Orderbooks 파일 목록 검색 (어제 날짜의 데이터만)
    csv_orderbooks_files = [f for f in os.listdir(csv_orderbooks_dir) if f.endswith('.csv') and is_yesterday(f)]
    csv_ticks_files = [f for f in os.listdir(csv_ticks_dir) if f.endswith('.csv') and is_yesterday(f)]
    tasks = []
    
    for csv_orderbook_file in csv_orderbooks_files:
        file_path = os.path.join(csv_orderbooks_dir, csv_orderbook_file)
        s3_file_name = f"csv/orderbooks/{csv_orderbook_file}"
        tasks.append(upload_to_s3(file_path, s3_file_name))
    
    for csv_tick_file in csv_ticks_files:
        file_path = os.path.join(csv_ticks_dir, csv_tick_file)
        s3_file_name = f"csv/ticks/{csv_tick_file}"
        tasks.append(upload_to_s3(file_path, s3_file_name))

    # CSV 내 Orderbooks와 Ticks 파일이 있을 경우 업로드 작업 실행
    if tasks:
        await asyncio.gather(*tasks)
    else:
        logging.info("No CSV Orderbooks or Ticks files found to upload for yesterday.")

# 메인 함수
async def main():
    await upload_orderbooks_and_ticks()
    await upload_csv_orderbooks_and_ticks()
    with open(log_file, "a") as log:
        log.write("\n")

# 실행
if __name__ == "__main__":
    asyncio.run(main())
