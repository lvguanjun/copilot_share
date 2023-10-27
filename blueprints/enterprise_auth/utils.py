#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/10/27 10:35:36
@Author  :   lvguanjun
@Desc    :   utils.py
"""

from flask_httpauth import HTTPBasicAuth

from config import ENTERPRISE_AUTH_USERS

auth = HTTPBasicAuth()


@auth.verify_password
def verify_pw(username, password):
    if not ENTERPRISE_AUTH_USERS:
        return True
    if (
        username in ENTERPRISE_AUTH_USERS
        and ENTERPRISE_AUTH_USERS[username] == password
    ):
        return True
    return False
