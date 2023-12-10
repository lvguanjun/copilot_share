#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   cache_token.py
@Time    :   2023/09/27 20:04:45
@Author  :   lvguanjun
@Desc    :   cache_token.py
"""


import random
import time

tokens = {}
err_tokens = {}


def set_token_to_cache(github_token, copilot_token):
    tokens[github_token] = copilot_token


def get_token_from_cache(github_token):
    # 当前过期时间30分钟，15-25分钟内随机值刷新
    # [(30 - 25) * 60, (30 - 15) * 60]
    extra_time = random.randint(300, 900)
    if copilot_token := tokens.get(github_token):
        if copilot_token["expires_at"] > int(time.time()) + extra_time:
            return copilot_token
    return None
