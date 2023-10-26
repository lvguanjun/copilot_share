#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   routes.py
@Time    :   2023/10/26 12:21:34
@Author  :   lvguanjun
@Desc    :   routes.py
"""

import logging
import random

from flask import jsonify, request

from blueprints.proxy import proxy_bp
from blueprints.proxy.utils import get_copilot_token, proxy_request
from cache.cache_token import err_tokens
from config import (
    CHAT_COMPLETION_ROUTE,
    CHAT_COMPLETION_URL,
    COMPLETION_ROUTE,
    COMPLETION_URL,
    GET_TOKEN_ROUTE,
    GITHUB_TOKEN,
    GPT_CHAT_URL,
    GPT_KEY,
    GPT_MODEL,
    TOKEN_MAX_ERR_COUNT,
    USE_GPT_PROXY,
)
from utils.decorators import auth_required, conditional_proxy_request
from utils.logger import log
from utils.utils import fake_request


@proxy_bp.route(GET_TOKEN_ROUTE, methods=["GET"])
@auth_required
async def get_token():
    """
    获取 copilot token
    """
    github_token_list = GITHUB_TOKEN.copy()
    while github_token_list:
        github_token = random.choice(github_token_list)
        status_code, copilot_token = await get_copilot_token(github_token)
        if status_code != 200:
            github_token_list.remove(github_token)
            # github token 请求失败次数达到阈值，则移除
            err_tokens[github_token] = err_tokens.get(github_token, 0) + 1
            if err_tokens[github_token] > TOKEN_MAX_ERR_COUNT:
                GITHUB_TOKEN.remove(github_token)
                log(f"WARNING: {github_token} has been removed", logging.WARNING)
            log(
                f"ERROR: {status_code} - {copilot_token} - {github_token}",
                logging.ERROR,
            )
            continue
        return jsonify(copilot_token)
    return jsonify({"msg": "Failed to get copilot token from all github token"}), 500


@proxy_bp.route(COMPLETION_ROUTE, methods=["POST"])
@conditional_proxy_request(COMPLETION_URL)
async def proxy_copilot_completion():
    """
    代理请求 copilot 的提示接口
    """
    res = await proxy_request(request, COMPLETION_URL)
    return res


@proxy_bp.route(CHAT_COMPLETION_ROUTE, methods=["POST"])
@conditional_proxy_request(CHAT_COMPLETION_URL)
async def proxy_copilot_chat_completion():
    """
    代理请求 copilot-chat 的提示接口
    """

    if USE_GPT_PROXY:
        max_retry = 3
        headers = {
            "Authorization": f"Bearer {GPT_KEY}",
            "content-type": "application/json",
        }
        json_data = request.get_json()
        json_data["model"] = GPT_MODEL
        new_request = fake_request("POST", headers=headers, json=json_data)
        res = await proxy_request(new_request, GPT_CHAT_URL, max_retry=max_retry)
    else:
        res = await proxy_request(request, CHAT_COMPLETION_URL)
    return res
