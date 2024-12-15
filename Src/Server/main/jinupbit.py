# Description: Upbit API와 비동기적으로 상호작용하여 호가창 데이터와 체결 데이터를 가져오는 스크립트

import jwt
import hashlib
import os
import requests
import uuid
from urllib.parse import urlencode, unquote
import info
import aiohttp

# Upbit API와 상호작용하는 클래스
class JinUpbit:

    access_key = ""
    secret_key = ""
    server_url = "https://api.upbit.com"

    # 생성자 - API 키 및 서버 URL 초기화
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.server_url = "https://api.upbit.com"
    
    # 비동기 GET 요청을 보내는 함수
    async def get(self, url, params, headers):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                res = await response.json()
                return res

    # 비동기적으로 호가 데이터를 가져오는 함수
    async def async_get_orderbook(self, symbol):
        headers = {"accept": "application/json"}
        params = ""
        res = await self.get(self.server_url + "/v1/orderbook" + "?markets=" + symbol + "&level=0", params, headers)

        return res

    # 비동기적으로 체결 데이터를 가져오는 함수
    async def async_get_ticks(self, market, to, count, cursor, days_ago):
        headers = {"accept": "application/json"}
        
        url = self.server_url + "/v1/trades/ticks" + "?market=" + market + "&count=100"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                res = await response.json()
                return res
