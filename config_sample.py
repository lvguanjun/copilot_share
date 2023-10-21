#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   config_sample.py
@Time    :   2023/09/28 23:24:26
@Author  :   lvguanjun
@Desc    :   config_sample.py
"""


# 服务器配置
server_config = {
    "host": "127.0.0.1",
    "port": 8080,
    "token": [
        "123456",
        "hello world",
    ],
}


# GITHUB接口相关

# 获取copilot token接口相关
GET_TOKEN_URL = "https://api.github.com/copilot_internal/v2/token"
GET_TOKEN_ROUTE = "/copilot_internal/v2/token"
GITHUB_TOKEN = [
    "gho_Fr0Xcd07iishNhaJuxOvvkwa6dzHKg2nrJeQ",
    "gho_Fr0XcdNjsbJKbcjauxOvvkwa6dzHKg2nrJeQ",
]

# 代码提示接口相关
COMPLETION_URL = (
    "https://copilot-proxy.githubusercontent.com/v1/engines/copilot-codex/completions"
)
COMPLETION_ROUTE = "/v1/engines/copilot-codex/completions"

# copilot-chat接口相关
CHAT_COMPLETION_URL = "https://api.githubcopilot.com/chat/completions"
CHAT_COMPLETION_ROUTE = "/chat/completions"


# 其他

# 一个github token最多请求失败次数
TOKEN_MAX_ERR_COUNT = 5

# log debug模式
LOG_DEBUG = False
