#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/10/26 11:40:08
@Author  :   lvguanjun
@Desc    :   utils.py
"""


import logging
import random
import string
from typing import Tuple

import aiohttp
import requests
from flask import Request, Response
from tenacity import retry, retry_if_result, stop_after_attempt, wait_fixed
from werkzeug.datastructures import Headers

from cache.cache_token import get_token_from_cache, set_token_to_cache
from config import CLEAR_HEADERS, GET_TOKEN_URL, PUBLIC_SUGGESTIONS
from utils.logger import log


async def get_copilot_token(github_token, get_token_url=GET_TOKEN_URL):
    copilot_token = get_token_from_cache(github_token)
    if not copilot_token:
        # 请求 github 接口获取 copilot_token
        headers = {
            "Authorization": f"token {github_token}",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(get_token_url, headers=headers) as res:
                if res.status != 200:
                    return res.status, await res.text()
                copilot_token = await res.json()
                copilot_token["telemetry"] = "disabled"
                copilot_token["public_suggestions"] = PUBLIC_SUGGESTIONS
                # 保存到 cache
                set_token_to_cache(github_token, copilot_token)
    return 200, copilot_token


async def proxy_request(
    request: Request, target_url: str, max_retry: int = 1
) -> Response:
    """
    Send a proxy request to the target URL.

    :param request: The request object to proxy.
    :param target_url: The target URL to proxy the request to.
    :param max_retry: The maximum number of retries to make.
    :return: status_code, response from the target server.
    """

    # 重试等待时间
    retry_wait = 0.5

    # 定义重试条件：仅当状态码200时不重试
    def retry_if_not_200(response):
        # 如果response为None（表示请求过程中出现异常），或者状态码不是200，那么触发重试
        return response is None or response.status_code != 200

    def retry_callback(retry_state):
        last_response = retry_state.outcome.result()
        return last_response

    @retry(
        retry=retry_if_result(retry_if_not_200),
        stop=stop_after_attempt(max_retry),
        wait=wait_fixed(retry_wait),
        retry_error_callback=retry_callback,
    )
    def _proxy_request(method, url, headers, data):
        try:
            resp = requests.request(
                method, url, headers=headers, data=data, stream=True
            )
            if resp.status_code != 200:
                log(f"{resp.status_code} - {resp.text}", logging.WARNING)
            return resp
        except Exception as e:
            log(f"ERROR: {e}", logging.ERROR)
            return None

    request_headers = Headers(request.headers)
    for header in CLEAR_HEADERS:
        request_headers.pop(header, None)
    request_headers = dict(request_headers)
    request_body = request.data
    request_method = request.method
    resp = _proxy_request(request_method, target_url, request_headers, request_body)
    if resp is not None:
        return Response(
            resp.iter_content(1024),
            content_type=resp.headers.get("content-type"),
            status=resp.status_code,
        )
    return Response("Failed to get response", status=500)


def gen_hex_str(length: int) -> str:
    return "".join(random.choice(string.hexdigits.lower()) for _ in range(length))


def create_headers(copilot_token: str) -> dict:
    return {
        "Authorization": f"Bearer {copilot_token}",
        "X-Request-Id": f"{gen_hex_str(8)}-{gen_hex_str(4)}-{gen_hex_str(4)}-{gen_hex_str(4)}-{gen_hex_str(12)}",
        "Vscode-Sessionid": f"{gen_hex_str(8)}-{gen_hex_str(4)}-{gen_hex_str(4)}-{gen_hex_str(4)}-{gen_hex_str(25)}",
        "Vscode-Machineid": f"{gen_hex_str(64)}",
        "Editor-Version": "vscode/1.83.1",
        "Editor-Plugin-Version": "copilot-chat/0.8.0",
        "Openai-Organization": "github-copilot",
        "Openai-Intent": "conversation-panel",
        "Content-Type": "application/json",
        "User-Agent": "GitHubCopilotChat/0.8.0",
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate,br",
        "connection": "close",
    }


def create_json_data(request: Request) -> Tuple[dict, bool]:
    json_data = request.json
    is_stream = json_data.get("stream", False)
    return {
        "messages": json_data.get("messages", []),
        "model": json_data.get("model", "copilot-chat"),
        "temperature": json_data.get("temperature", 0.1),
        "top_p": json_data.get("top_p", 1),
        "n": json_data.get("n", 1),
        "stream": is_stream,
        "intent": True,
    }, is_stream
