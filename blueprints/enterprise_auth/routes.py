#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   routes.py
@Time    :   2023/10/26 20:28:35
@Author  :   lvguanjun
@Desc    :   routes.py
"""

from flask import jsonify, request

from blueprints.enterprise_auth import enterprise_auth_bp
from blueprints.enterprise_auth.utils import auth
from config import server_config


@enterprise_auth_bp.route("/login/device/code", methods=["POST"])
async def get_device_code_post():
    verification_uri = f"{request.url_root}login/device"
    return jsonify(
        {
            "device_code": "H9lX3aAH6FxMOAzeQlqa",
            "expires_in": 1800,
            "interval": 3,
            "user_code": "MHUA-ZKH3",
            "verification_uri": verification_uri,
            "verification_uri_complete": f"{verification_uri}?user_code=MHUA-ZKH3",
        }
    )


@enterprise_auth_bp.route("/login/device", methods=["GET"])
async def get_device_code_get():
    return "Login successful, you can now close this page!"


@enterprise_auth_bp.route("/login/oauth/access_token", methods=["POST"])
@auth.login_required
async def get_access_token():
    custom_token = "ghu_notNeedToken"
    if custom_token := server_config["token"]:
        custom_token = custom_token[0]
    return jsonify(
        {
            "access_token": custom_token,
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
            "login": "copilot_enterprise",
            "name": "copilot_enterprise",
        }
    )


@enterprise_auth_bp.route("/api/v3/meta", methods=["GET"])
async def get_meta():
    return jsonify({})
