#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   routes.py
@Time    :   2023/09/27 13:42:00
@Author  :   lvguanjun
@Desc    :   routes.py
"""


import logging
import random

from flask import Flask, jsonify, request

from cache.cache_token import err_tokens
from config import (
    CHAT_COMPLETION_ROUTE,
    CHAT_COMPLETION_URL,
    COMPLETION_ROUTE,
    COMPLETION_URL,
    GET_TOKEN_ROUTE,
    GITHUB_TOKEN,
    NEED_TELEMETRY,
    TELEMETRY_ROUTE,
    TELEMETRY_URL,
    TOKEN_MAX_ERR_COUNT,
    server_config,
)
from proxy.github import get_copilot_token
from proxy.proxy import proxy_request
from utils.decorators import auth_required
from utils.logger import log

app = Flask(__name__)


@app.route(GET_TOKEN_ROUTE, methods=["GET"])
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


@app.route(COMPLETION_ROUTE, methods=["POST"])
async def proxy_copilot_completion():
    """
    代理请求 copilot 的提示接口
    """
    res = await proxy_request(request, COMPLETION_URL)
    return res


@app.route(TELEMETRY_ROUTE, methods=["POST"])
async def proxy_copilot_telemetry():
    """
    代理请求 copilot 的遥测接口
    若不需要遥测，则直接返回 200
    """
    if not NEED_TELEMETRY:
        return jsonify({}), 200
    res = await proxy_request(request, TELEMETRY_URL)
    return res


@app.route(CHAT_COMPLETION_ROUTE, methods=["POST"])
async def proxy_copilot_chat_completion():
    """
    代理请求 copilot-chat 的提示接口
    """
    res = await proxy_request(request, CHAT_COMPLETION_URL)
    return res


@app.before_request
def log_unmatched_routes():
    """
    记录未匹配到的路由，并返回 404
    """
    if request.endpoint is None:
        log(f"Unmatched request: {request.method} {request.url}", logging.WARNING)
        log(f"Request headers: {request.headers}", logging.DEBUG)
        log(f"Request body: {request.data}", logging.DEBUG)
        err_msg = {
            "documentation_url": "https://docs.github.com/rest",
            "message": "Not Found",
        }
        return jsonify(err_msg), 404


if __name__ == "__main__":
    app.run(host=server_config["host"], port=server_config["port"], debug=False)
