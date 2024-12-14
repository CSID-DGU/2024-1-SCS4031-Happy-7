# Description: 호가창, 체결데이터가 제대로 전처리 계산되어 병합되고 있는지 확인하기 위해 csv파일로 현황을 볼 수 있는 스크립트

import asyncio 
import pandas as pd
import traceback
from collections import deque
import jinupbit

# Upbit API 객체 초기화
jupbit = jinupbit.JinUpbit("", "")

# 큐 크기 제한 설정
ORDERBOOK_QUEUE_LIMIT = 210
TICK_QUEUE_LIMIT = 210

# 주문서 및 체결 데이터 큐 초기화
orderbook_queue = deque(maxlen=ORDERBOOK_QUEUE_LIMIT)
ticks_queue = deque(maxlen=TICK_QUEUE_LIMIT)

# 전처리 함수 - 주문서 데이터
def preprocess_orderbook(orderbook_data):
    orderbook_data['spread'] = orderbook_data['orderbook_units'][0]['ask_price'] - orderbook_data['orderbook_units'][0]['bid_price']
    orderbook_data['mid_price'] = (orderbook_data['orderbook_units'][0]['ask_price'] + orderbook_data['orderbook_units'][0]['bid_price']) / 2
    orderbook_data['obi'] = (orderbook_data['total_bid_size'] - orderbook_data['total_ask_size']) / \
                            (orderbook_data['total_bid_size'] + orderbook_data['total_ask_size'])
    return {
        "timestamp": orderbook_data['timestamp'],
        "spread": orderbook_data['spread'],
        "mid_price": orderbook_data['mid_price'],
        "obi": orderbook_data['obi']
    }

# ticks 데이터에서 추가적인 feature 추출 (가격 변동성, 매수/매도 비율 등)
def preprocess_ticks(ticks_df):
    # 입력이 DataFrame인지 확인
    if not isinstance(ticks_df, pd.DataFrame):
        ticks_df = pd.DataFrame(ticks_df)

    if len(ticks_df) >= 30:  # 최소 30개의 데이터가 있어야 rolling 연산 가능
        # 최근 30개 거래 가격의 가격 변동성 (표준편차)
        ticks_df['price_volatility'] = ticks_df['trade_price'].rolling(window=30).std()
        # 최근 30개 거래의 매수/매도 비율
        ticks_df['buy_sell_ratio'] = ticks_df['ask_bid'].rolling(window=30).mean()
        # 최근 30개 거래 가격의 변동률 (변동폭)
        ticks_df['price_change_rate'] = (
            ticks_df['trade_price']
            .rolling(window=30)
            .apply(lambda x: (x.max() - x.min()) / x.max() if x.max() > 0 else 0, raw=True)
        )
    else:  # 데이터가 부족하면 NaN으로 채우기
        ticks_df['price_volatility'] = None
        ticks_df['buy_sell_ratio'] = None
        ticks_df['price_change_rate'] = None

    # 필요한 컬럼만 반환
    required_columns = ['timestamp', 'trade_price', 'price_volatility', 'buy_sell_ratio', 'price_change_rate']
    for col in required_columns:
        if col not in ticks_df.columns:
            ticks_df[col] = None

    return ticks_df[required_columns]

# Upbit 호가 데이터를 수집하는 비동기 함수
async def upbit_get_orderbook():
    global orderbook_queue
    try:
        bf_timestamp = 0
        while True:
            # Upbit API로 호가 데이터 수집
            upbit_res = await jupbit.async_get_orderbook("KRW-BTC")

            if isinstance(upbit_res, dict):
                continue
            
            upbit_res = upbit_res[0]
            if bf_timestamp >= int(upbit_res['timestamp']):
                await asyncio.sleep(0.2)
                continue
            
            bf_timestamp = int(upbit_res['timestamp'])

            # 데이터 전처리
            processed_data = preprocess_orderbook(upbit_res)

            # 큐에 데이터 추가 (메인 끝에 추가)
            orderbook_queue.append(processed_data)

            await asyncio.sleep(0.2)
    except Exception as e:
        print(f"Orderbook Error: {e}")

# Upbit 체결 데이터를 수집하는 비동기 함수
async def upbit_get_ticks():
    global ticks_queue
    try:
        bf_sequential_id = 0
        while True:
            # Upbit API로 체결 데이터 수집
            upbit_res = await jupbit.async_get_ticks("KRW-BTC", "", "", "", "")

            for r in upbit_res:
                if bf_sequential_id < r['sequential_id']:
                    bf_sequential_id = r['sequential_id']

                    # 전처리를 위해 큐에 추가
                    ticks_queue.append({
                        "timestamp": r['timestamp'],
                        "trade_price": r['trade_price'],
                        "ask_bid": 1 if r['ask_bid'] == 'BID' else 0  # 매수: 1, 매도: 0
                    })

            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"Tick Error: {e}")

# 호가 데이터와 체결 데이터를 병합하고 저장하는 함수
async def merge_and_save():
    try:
        global orderbook_queue, ticks_queue

        # 큐 데이터를 DataFrame으로 변환
        orderbook_df = pd.DataFrame(list(orderbook_queue))
        ticks_df = pd.DataFrame(list(ticks_queue))

        # ticks 데이터 전처리
        processed_ticks_df = preprocess_ticks(ticks_df)

        # 두 데이터를 타임스탬프를 기준으로 병합
        if not orderbook_df.empty and not processed_ticks_df.empty:
            merged_data = pd.merge_asof(orderbook_df.sort_values('timestamp'), 
                                        processed_ticks_df.sort_values('timestamp'), 
                                        on='timestamp', 
                                        direction='nearest')

            # 병합된 데이터를 CSV로 저장 (기존 merge.csv 파일 덮어쓰기)
            merged_data.to_csv("/home/ubuntu/project/data/queue/queue.csv", index=False)
    except Exception as e:
        print(f"Merge Error: {e}")

# 메인 함수
async def main():
    try:
        tasks = [
            asyncio.create_task(upbit_get_orderbook()),
            asyncio.create_task(upbit_get_ticks()),
            asyncio.create_task(periodic_merge_and_save())
        ]
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f"Main Procedure Error: {e}")

# 병합 작업을 주기적으로 수행하는 함수
async def periodic_merge_and_save():
    while True:
        await merge_and_save()
        await asyncio.sleep(0.2)  # 0.2초마다 병합 수행

if __name__ == "__main__":
    asyncio.run(main())
