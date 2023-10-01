#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   github.py
@Time    :   2023/09/27 20:02:02
@Author  :   lvguanjun
@Desc    :   github.py
"""

import aiohttp

from cache.cache_token import get_token_from_cache, set_token_to_cache
from config import GET_TOKEN_URL


async def get_copilot_token(github_token):
    copilot_token = get_token_from_cache(github_token)
    if not copilot_token:
        # 请求 github 接口获取 copilot_token
        headers = {
            "Authorization": f"token {github_token}",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(GET_TOKEN_URL, headers=headers) as res:
                if res.status != 200:
                    return res.status, await res.text()
                copilot_token = await res.json()
                # 保存到 cache
                set_token_to_cache(github_token, copilot_token)
    return 200, copilot_token
