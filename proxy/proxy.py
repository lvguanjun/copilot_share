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


async def proxy_request(request: Request, target_url: str) -> Response:
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
        stream=True,
    )
    content_type = resp.headers.get("Content-Type", "").lower()
    resp_headers = dict(resp.headers)

    # SEE响应需要分块传输
    if content_type == "text/event-stream":

        def generate():
            try:
                for line in resp.iter_lines():
                    if line:
                        if line[0:12] == b"data: [DONE]":
                            yield b"data: [DONE]\n\n"
                            break
                        yield line + b"\n\n"
            finally:
                resp.close()

        return Response(generate(), status=resp.status_code, headers=resp_headers)
    else:
        response = Response(resp.content, status=resp.status_code, headers=resp_headers)
        resp.close()
        return response
