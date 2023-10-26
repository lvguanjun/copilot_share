#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   factory.py
@Time    :   2023/10/26 18:54:17
@Author  :   lvguanjun
@Desc    :   factory.py
"""

from flask import Flask

from blueprints.proxy import proxy_bp


def create_app():
    app = Flask(__name__)
    # 加载配置

    # 注册蓝本
    app.register_blueprint(proxy_bp)

    # 初始化扩展

    return app
