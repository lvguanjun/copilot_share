#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   copilot.py
@Time    :   2023/09/27 21:04:48
@Author  :   lvguanjun
@Desc    :   copilot.py
"""

import logging

import requests
from flask import Request, Response
from tenacity import retry, retry_if_result, stop_after_attempt, wait_fixed

from utils.logger import log


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

    request_headers = dict(request.headers)
    request_headers.pop("Host", None)
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
