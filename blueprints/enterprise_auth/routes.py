#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   routes.py
@Time    :   2023/10/26 20:28:35
@Author  :   lvguanjun
@Desc    :   routes.py
"""

from flask import jsonify

from blueprints.enterprise_auth import enterprise_auth_bp
from config import ENTERPRISE_AUTH_DOMAIN


@enterprise_auth_bp.route("/login/device/code", methods=["POST"])
async def get_device_code_post():
    return jsonify(
        {
            "device_code": "H9lX3aAH6FxMOAzeQlqa",
            "expires_in": 1800,
            "interval": 3,
            "user_code": "MHUA-ZKH3",
            "verification_uri": f"http://{ENTERPRISE_AUTH_DOMAIN}/login/device",
            "verification_uri_complete": (
                f"http://{ENTERPRISE_AUTH_DOMAIN}/login/device?user_code=MHUA-ZKH3"
            ),
        }
    )


@enterprise_auth_bp.route("/login/device", methods=["GET"])
async def get_device_code_get():
    return "Login successful, you can now close this page!"


@enterprise_auth_bp.route("/login/oauth/access_token", methods=["POST"])
async def get_access_token():
    return jsonify(
        {
            "access_token": "123456",
            "scope": "user:email",
            "token_type": "bearer",
        }
    )


@enterprise_auth_bp.route("/api/v3/user", methods=["GET"])
async def get_user():
    return jsonify(
        {
            "email": "shared@example.com",
            "id": "504573ef6e0bdff9",
            "login": "Copilot_example",
            "name": "Copilot_example",
        }
    )


@enterprise_auth_bp.route("/api/v3/meta", methods=["GET"])
async def get_meta():
    return jsonify({})
