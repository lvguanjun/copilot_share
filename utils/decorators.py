#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   decorators.py
@Time    :   2023/09/27 13:52:49
@Author  :   lvguanjun
@Desc    :   decorators.py
"""


import logging
from functools import wraps

from flask import jsonify, redirect, request

from config import PROXY_COMPLETION_REQUEST, server_config
from utils.logger import log


def auth_required(fun):
    @wraps(fun)
    async def wrapper(*args, **kwargs):
        token = server_config.get("token")
        custom_token = request.headers.get("Authorization")
        if not token or custom_token in (f"token {t}" for t in token):
            return await fun(*args, **kwargs)
        err_msg = {
            "msg": "token error",
            "documentation_url": "https://docs.github.com/rest",
        }
        log(f"Custom token is not correct: {custom_token}", logging.WARNING)
        return jsonify(err_msg), 401

    return wrapper


def conditional_proxy_request(request_url):
    def decorator(fun):
        @wraps(fun)
        async def wrapper(*args, **kwargs):
            if PROXY_COMPLETION_REQUEST:
                return await fun(*args, **kwargs)
            return redirect(request_url, code=307)

        return wrapper

    return decorator
