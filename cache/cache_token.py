#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   cache_token.py
@Time    :   2023/09/27 20:04:45
@Author  :   lvguanjun
@Desc    :   cache_token.py
"""


import time

tokens = {}
err_tokens = {}


def set_token_to_cache(github_token, copilot_token):
    tokens[github_token] = copilot_token


def get_token_from_cache(github_token):
    if copilot_token := tokens.get(github_token):
        if copilot_token["expires_at"] > int(time.time()) + 60:
            return copilot_token
    return None
