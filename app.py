#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   routes.py
@Time    :   2023/09/27 13:42:00
@Author  :   lvguanjun
@Desc    :   routes.py
"""


import asyncio
import logging

from flask import jsonify, request

from config import server_config
from factory import create_app
from utils.client_manger import client_manager
from utils.logger import log

app = create_app()


@app.before_request
async def log_unmatched_routes():
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
    try:
        app.run(
            host=server_config["host"],
            port=server_config["port"],
            debug=False,
        )
    finally:
        asyncio.run(client_manager.close())
