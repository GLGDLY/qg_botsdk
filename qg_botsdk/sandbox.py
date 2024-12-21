#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, List, Optional, Iterable

from ._statics import EVENTS
from ._utils import exception_handler
from .logger import Logger


class SandBox:
    def __init__(
        self,
        guilds: Optional[List[str]] = None,
        guild_users: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        q_users: Optional[List[str]] = None,
    ):
        """ "
        沙箱模式配置项，当BOT(..., is_sandbox=True)时，只有列表中指定的频道、群、用户可以接收到消息；
        当为False（非沙箱环境）时，过滤掉列表中指定频道、群、用户的消息。

        :param guilds: 设置为沙箱的频道ID列表
        :param guild_users: 设置为沙箱的频道私信用户ID列表
        :param groups: 设置为沙箱的群ID列表
        :param q_users: 设置为沙箱的QQ私信用户ID列表
        """
        self.guilds = self.__to_set(guilds)
        self.guild_users = self.__to_set(guild_users)
        self.groups = self.__to_set(groups)
        self.q_users = self.__to_set(q_users)

        self.is_sandbox = False
        self.logger: Optional[Logger] = None

    @staticmethod
    def __to_set(data: Optional[List[str]]) -> set:
        if isinstance(data, Iterable):
            return set(data)
        return set()

    def set_logger(self, logger):
        self.logger = logger

    def set_is_sandbox(self, is_sandbox: bool):
        self.is_sandbox = is_sandbox

    def checker(self, event: EVENTS, data: dict) -> bool:
        try:
            if event == EVENTS.MESSAGE_CREATE:
                return (data["d"]["guild_id"] not in self.guilds) ^ self.is_sandbox
            elif event == EVENTS.DM_CREATE:
                return (data["d"]["author"]["id"] not in self.guild_users) ^ self.is_sandbox
            elif event == EVENTS.GROUP_AT_MESSAGE_CREATE:
                return (data["d"]["group_openid"] not in self.groups) ^ self.is_sandbox
            elif event == EVENTS.C2C_MESSAGE_CREATE:
                return (data["d"]["author"]["id"] not in self.q_users) ^ self.is_sandbox
        except Exception as e:
            if self.logger:
                self.logger.error(f"沙箱模式检查失败，已放行：{repr(e)}")
                self.logger.debug(f"事件：{event}, 数据：{data}")
                self.logger.error(exception_handler(e))
            return True
