#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   factory.py
@Time    :   2023/10/26 18:54:17
@Author  :   lvguanjun
@Desc    :   factory.py
"""

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from blueprints.enterprise_auth import enterprise_auth_bp
from blueprints.proxy import proxy_bp
from config import USE_ENTERPRISE_AUTH


def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # 支持反向代理
    # 加载配置

    # 注册蓝图
    app.register_blueprint(proxy_bp)
    if USE_ENTERPRISE_AUTH:
        app.register_blueprint(enterprise_auth_bp)

    # 初始化扩展

    return app
