#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   decorators.py
@Time    :   2023/09/27 13:52:49
@Author  :   lvguanjun
@Desc    :   decorators.py
"""


from functools import wraps
import logging

from flask import jsonify, request

from config import server_config
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
