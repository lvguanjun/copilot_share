#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/10/26 11:40:08
@Author  :   lvguanjun
@Desc    :   utils.py
"""


import asyncio
import logging
import queue
import threading
from typing import Optional

import httpx
from flask import Request, Response
from tenacity import retry, retry_if_result, stop_after_attempt, wait_fixed
from werkzeug.datastructures import Headers

from cache.cache_token import get_token_from_cache, set_token_to_cache
from config import CLEAR_HEADERS, GET_TOKEN_URL
from utils.client_manger import client_manager
from utils.logger import log


async def get_copilot_token(github_token, get_token_url=GET_TOKEN_URL):
    copilot_token = get_token_from_cache(github_token)
    if not copilot_token:
        # 请求 github 接口获取 copilot_token
        headers = {
            "Authorization": f"token {github_token}",
        }
        res = await client_manager.client.get(get_token_url, headers=headers)
        if res.status_code != 200:
            return res.status_code, res.text()
        copilot_token = res.json()
        # 保存到 cache
        set_token_to_cache(github_token, copilot_token)
    return 200, copilot_token


async def send_request(method: str, url: str, headers: dict, data: bytes):
    try:
        req = client_manager.client.build_request(
            method, url, headers=headers, data=data
        )
        return await client_manager.client.send(req, stream=True)
    except Exception as e:
        log(f"ERROR: {e}", logging.ERROR)
        return None


def stream_response(response: httpx.Response):
    q = queue.Queue()

    async def fetch_chunks():
        try:
            async for chunk in response.aiter_bytes():
                q.put(chunk)
        finally:
            await response.aclose()
            q.put(None)  # Signal the end of the stream

    def run_fetch_chunks():
        asyncio.run(fetch_chunks())

    threading.Thread(target=run_fetch_chunks).start()

    def generator():
        while True:
            chunk = q.get()
            if chunk is None:
                break
            yield chunk

    return Response(
        response=generator(),
        status=response.status_code,
        headers=dict(response.headers),
    )


def should_retry(response: Optional[httpx.Response]) -> bool:
    return response is None


async def proxy_request(request: Request, target_url: str, max_retry: int = 3):
    wait_time = 0.5
    retry_time = 1

    def capture_retry_time(retry_state):
        nonlocal retry_time
        retry_time = retry_state.attempt_number

    @retry(
        retry=retry_if_result(should_retry),
        stop=stop_after_attempt(max_retry),
        wait=wait_fixed(wait_time),
        before=capture_retry_time,
    )
    async def _proxy_request(request: Request, target_url: str):
        request_headers = Headers(request.headers)
        for header in CLEAR_HEADERS:
            request_headers.pop(header, None)
        request_headers = dict(request_headers)
        request_body = request.data
        request_method = request.method

        response = await send_request(
            request_method, target_url, request_headers, request_body
        )
        if response is None:
            if retry_time == max_retry:
                return Response("Failed to get response", status=500)
            return None
        if response.status_code != 200 and retry_time < max_retry:
            log(f"{response.status_code=}, {retry_time} retrying...", logging.WARNING)
            await response.aclose()
            return None
        return stream_response(response)

    response = await _proxy_request(request, target_url)

    return response
