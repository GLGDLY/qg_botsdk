# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
qg_botsdk Library
~~~~~~~~~~~~~~~~~~~~~

一款简洁、容易上手，适用于QQ官方频道机器人的Python轻量级SDK；只需导入qg_botsdk.qg_bot.BOT即可快速使用

.. seealso::
    更多教程和相关资讯可参阅：
    https://thoughts.teambition.com/sharespace/6289c429eb27e90041a58b57/docs/6289c429eb27e90041a58b52

:copyright: (c) 2022 by GLGDLY.
:license: MIT, see LICENSE for more details.
"""

from .qg_bot import BOT, version
from .model import Model
from .logger import Logger

__title__ = "requests"
__version__ = version
__description__ = "easy-to-use SDK for Tencent QQ guild robot"
__url__ = "https://github.com/GLGDLY/qg_botsdk"
__author__ = "GDLY"
__author_email__ = "tzlgdly@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2022 GLGDLY"


name = "qg_botsdk"
__all__ = ("BOT", "Model", "Logger")
