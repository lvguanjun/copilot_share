#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   __init__.py
@Time    :   2023/10/26 12:18:11
@Author  :   lvguanjun
@Desc    :   __init__.py
"""

from flask import Blueprint

proxy_bp = Blueprint("proxy", __name__)

from . import routes, utils
