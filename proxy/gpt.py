#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   gpt.py
@Time    :   2023/10/21 22:03:19
@Author  :   lvguanjun
@Desc    :   gpt.py
"""

import logging

import requests
from flask import Response

from config import GPT_CHAT_ROUTE, GPT_KEY, GPT_URL
from utils.logger import log


async def proxy_gpt(request, model: str = "gpt-4-32k"):
    body = request.get_json()
    body["model"] = model
    headers = {
        "Authorization": f"Bearer {GPT_KEY}",
        "content-type": "application/json",
    }
    MAX_RETRIES = 3
    for _ in range(MAX_RETRIES):
        except_flag = False
        try:
            resp = requests.post(
                f"{GPT_URL}{GPT_CHAT_ROUTE}", json=body, headers=headers
            )
            if resp.status_code == 200:
                return Response(
                    resp.iter_content(1024),
                    content_type=resp.headers.get("content-type"),
                    status=resp.status_code,
                )
            log(f"{resp.status_code} - {resp.text}", logging.WARNING)
        except Exception as e:
            except_flag = True
            log(f"ERROR: {e}", logging.ERROR)
    if not except_flag:
        return Response(
            resp.iter_content(1024),
            content_type=resp.headers.get("content-type"),
            status=resp.status_code,
        )
    return Response("Failed to get response from GPT", status=500)
