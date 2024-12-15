# Description: Upbit에서 호가창 데이터와 체결 데이터를 수집하여 학습을 위한 최종 데이터를 생성하는 스크립트

import os
import time
import json
import log
import asyncio
from datetime import datetime
import traceback
import subprocess
import aiofiles
import jinupbit

engine = None
log = log.Log("orderbook_monitoring")

# 데이터 수집 엔진 클래스 정의
class Engine():
    rd = None
    jbinance = None
    jupbit = None
    jbithumb = None
    all_datas_coin_manage_mas = None

    def __init__(self):
        # Upbit API 객체 초기화
        self.jupbit = jinupbit.JinUpbit("", "")

# Upbit 호가 데이터를 수집하는 비동기 함수
async def upbit_get_orderbook():

    global engine

    before_date = datetime.today()
    date = before_date.strftime('%Y%m%d')
    file_name = "/home/ubuntu/project/data/raw/orderbooks/" + date + ".txt"

    try:
        bf_timestamp = 0
        while True:
            
            # 비트코인 호가 데이터 비동기 수집
            a = asyncio.create_task(engine.jupbit.async_get_orderbook("KRW-BTC"))
            upbit_res = await a

            # 응답이 dictionary인 경우 예외 처리
            if(isinstance(upbit_res,dict)):
                await exception_func(str(upbit_res), "Orderbook Error","upbit_get_orderbook")

            # 이전 timestamp보다 작거나 같으면 다음으로
            if bf_timestamp >= int(upbit_res[0]['timestamp']):
                await asyncio.sleep(0.2)
                continue

            # 현재 timestamp 업데이트
            bf_timestamp = int(upbit_res[0]['timestamp'])
            upbit_res = upbit_res[0]
            
            # 불필요한 key 제거
            upbit_res.pop('level', None)
            upbit_res.pop('market', None)
            
            # 파일에 호가 데이터 저장
            async with aiofiles.open(file_name, 'a') as file:
                await file.write(str(upbit_res) + "\n")

            await asyncio.sleep(0.2)

    except Exception as e:
        file.close()
        await exception_func(e, "Orderbook Error","upbit_get_orderbook")

# Upbit 체결 데이터를 수집하는 비동기 함수
async def upbit_get_ticks():
    
    global engine
    
    before_date = datetime.today()
    date = before_date.strftime('%Y%m%d')
    file_name = "/home/ubuntu/project/data/raw/ticks/" + date + ".txt"

    try:
        bf_sequential_id = 0
        while True:

            # Upbit 체결 데이터 비동기 수집
            upbit_res = await engine.jupbit.async_get_ticks("KRW-BTC","","","","")

            for r in upbit_res:
                if bf_sequential_id < r['sequential_id']:
                    bf_sequential_id = r['sequential_id']
                    
                    # 불필요한 key 제거
                    r.pop('trade_date_utc', None)
                    r.pop('trade_time_utc', None)
                    r.pop('sequential_id', None)
                    r.pop('market', None)
                    
                    # 파일에 체결 데이터 저장
                    async with aiofiles.open(file_name, 'a') as file:
                        await file.write(str(r) + "\n")

            await asyncio.sleep(0.5)

    except Exception as e:
        file.close()
        await exception_func(e, "Orderbook Error","upbit_get_orderbook")

# 예외 처리 및 재시작 함수
async def exception_func(e, title, info):

    traceback_info = traceback.format_exc()
    log.log("traceback : " + str(traceback_info))
    log.log("e : " + str(e))
    log.log("title : " + str(title))
    log.log("info : " + str(info))
    
    # 에러 로그 작성 후 시스템 재시작
    email_info = "title : " + str(title) + "\n"
    email_info += "info : " + str(info) + "\n"

    system_input = "nohup python3 -u /home/ubuntu/project/codes/main/orderbook_monitoring.py 2>&1 &"
    os.system(system_input)
    quit()

# 프로세스 제어 함수
async def process_control():

    my_pid = os.getpid()

    # 현재 실행 중인 프로세스 찾기
    cmd = 'ps -ef | grep -w "python3.*orderbook_monitoring.py" | grep -v grep'

    result = subprocess.run(cmd, shell=True,capture_output=True)

    result = str(result.stdout.decode())
    result_next_line = result.split('\n')

    for r in result_next_line:
        each_result = r.split()

        # 동일한 프로세스를 종료
        if len(r) > 0:
            if int(my_pid) != int(each_result[1]):
                log.log("kill start : " + str(each_result[1]))
                os.system("kill -9 " + str(each_result[1]))

    before_date = datetime.today()
    while True:
        await asyncio.sleep(1)
        after_date = datetime.today()
        diff = int(before_date.strftime('%Y%m%d')) - int(after_date.strftime('%Y%m%d'))
        
        # 날짜가 변경되면 예외 처리
        if diff != 0:
            await exception_func("", "Orderbook 날짜변경","date change")

async def main_procedure():
    try:
        log.log("main_procedure start")
        
        async_list = list()

        async_list.append(asyncio.create_task(upbit_get_ticks()))
        async_list.append(asyncio.create_task(upbit_get_orderbook()))

        for a in async_list:
            await a

        log.log("main_procedure end")
    except Exception as e:
        await exception_func(e, "Orderbook Error","main_procedure")

# 초기화 함수
async def init():

    log.log("init start")

    async_list = list()

    async_list.append(asyncio.create_task(process_control()))
    async_list.append(asyncio.create_task(main_procedure()))
    
    for a in async_list:
        await a

    log.log("init end")

if __name__ == "__main__":

    engine = Engine()
    asyncio.run(init())
