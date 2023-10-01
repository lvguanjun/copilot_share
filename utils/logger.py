#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   logger.py
@Time    :   2023/09/27 16:17:58
@Author  :   lvguanjun
@Desc    :   logger.py
"""

import logging
from concurrent.futures import ThreadPoolExecutor

from config import LOG_DEBUG

logger = logging.getLogger(__name__)
if LOG_DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

executor = ThreadPoolExecutor(max_workers=1)


def log(msg, level=logging.INFO):
    def _log():
        if level == logging.DEBUG:
            logger.debug(msg)
        elif level == logging.INFO:
            logger.info(msg)
        elif level == logging.WARNING:
            logger.warning(msg)
        elif level == logging.ERROR:
            logger.error(msg)
        elif level == logging.CRITICAL:
            logger.critical(msg)

    executor.submit(_log)
