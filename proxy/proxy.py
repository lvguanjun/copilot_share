#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   copilot.py
@Time    :   2023/09/27 21:04:48
@Author  :   lvguanjun
@Desc    :   copilot.py
"""

import requests
from flask import Request, Response


async def proxy_request(request: Request, target_url: str):
    """
    Send a proxy request to the target URL.

    :param request: The request object to proxy.
    :param target_url: The target URL to proxy the request to.
    :return: status_code, response from the target server.
    """
    request_headers = dict(request.headers)
    request_headers.pop("Host", None)
    request_body = request.data
    request_method = request.method
    resp = requests.request(
        request_method,
        target_url,
        headers=request_headers,
        data=request_body,
    )
    data = resp.content
    status_code = resp.status_code
    headers = dict(resp.headers)
    res = Response(data, status_code, headers=headers)
    if res.headers.get("Transfer-Encoding") == "chunked":
        res.headers.pop("Content-Length")
    res.automatically_set_content_length = False
    return res

    # 能力不足，异步疯狂报错，怀疑可能是网络原因 + 异步请求 导致的
    # 暂存这部分代码，后续排查

    # async with aiohttp.ClientSession() as session:
    #     for i in range(MAX_RETRIES):
    #         try:
    #             async with session.request(
    #                 request_method,
    #                 target_url,
    #                 headers=request_headers,
    #                 data=request_body,
    #             ) as resp:
    #                 data = await resp.read()
    #                 status_code = resp.status
    #                 headers = dict(resp.headers)
    #                 res = Response(data, status_code, headers=headers)
    #                 if res.headers.get("Transfer-Encoding"):
    #                     res.headers.pop("Content-Length")
    #                 res.automatically_set_content_length = False
    #                 return res
    #         except aiohttp.ServerConnectionError:
    #             continue
    #     return Response("Server Connection Error", 500)
