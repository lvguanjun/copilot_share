#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   __init__.py
@Time    :   2023/10/26 20:14:54
@Author  :   lvguanjun
@Desc    :   __init__.py
"""

from flask import Blueprint

enterprise_auth_bp = Blueprint("enterprise_auth", __name__)

from . import routes
