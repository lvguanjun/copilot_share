#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   client_manger.py
@Time    :   2023/10/30 11:25:51
@Author  :   lvguanjun
@Desc    :   client_manger.py
"""

import httpx


class ClientManager:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = httpx.AsyncClient()
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


client_manager = ClientManager()
