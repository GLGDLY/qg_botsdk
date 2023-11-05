#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
qg_botsdk Library
~~~~~~~~~~~~~~~~~~~~~

一款简洁、容易上手，适用于QQ官方频道机器人的Python轻量级SDK；只需导入qg_botsdk.qg_bot.BOT即可快速使用

.. seealso::
    更多教程和相关资讯可参阅：
    https://qg-botsdk.readthedocs.io/zh_CN/latest/index.html

:copyright: (c) 2022 by GLGDLY.
:license: MIT, see LICENSE for more details.
"""

from . import utils
from ._exception import IdTokenError, IdTokenMissing, WaitTimeoutError
from .api_model import ApiModel
from .logger import Logger
from .model import (
    BotCommandObject,
    EmojiID,
    EmojiString,
    Model,
    Scope,
    SessionObject,
    SessionStatus,
)
from .plugins import Plugins
from .qg_bot import BOT
from .version import __version__

__title__ = "qg_botsdk"
__description__ = "easy-to-use SDK for Tencent QQ guild robot"
__url__ = "https://github.com/GLGDLY/qg_botsdk"
__author__ = "GDLY"
__author_email__ = "tzlgdly@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2022 GLGDLY"


name = "qg_botsdk"
__all__ = (
    "BOT",
    "Model",
    "ApiModel",
    "Scope",
    "SessionObject",
    "SessionStatus",
    "BotCommandObject",
    "EmojiID",
    "EmojiString",
    "Logger",
    "Plugins",
    "utils",
    "IdTokenMissing",
    "IdTokenError",
    "WaitTimeoutError",
)
