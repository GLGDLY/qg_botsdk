#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, Hashable, Optional

from ._statics import TraceNames
from ._utils import TraceCallerData, stack_exception_handler
from .model import Scope, SessionObject, SessionStatus


class AbstractSessionManager:
    """
    Session Manager用于管理在不同作用域（scope）下的 sessions，主要用处为存储运行时的临时数据。

    注意：为允许session可以保存class实例等py数据类型，session的数据以pickle方式保存
    """

    # -*- session manage methods -*-
    def new(
        self,
        scope: Scope,
        key: Hashable,
        data: Dict = None,
        identify: Hashable = None,
        is_replace: bool = True,
        timeout: Optional[float] = None,
        timeout_reply: str = None,
        inactive_gc_timeout: Optional[float] = 0,
    ) -> SessionObject:
        """
        根据scope作用域和相应的key，创建一个新的session（可用于间保存和传递字典的k-v pair数据）

        :param scope: 作用域(USER, GUILD, CHANNEL, GLOBAL)
        :param key: session的键，要求为可哈希对象，根据键在作用域下创建session
        :param data: session保存的字典类型数据，可选
        :param identify: scope作用域下的标识，不填时从栈查找本次的消息数据并自动填入（如Scope.USER会为此项自动填入user id），可选
        :param is_replace: 是否替换已存在的session，False且已存在相应key的session时报错，可选
        :param timeout: session处于ACTIVE状态下转为INACTIVE的超时时间，单位秒，None为没有超时，可选
        :param timeout_reply: 当session超时（从ACTIVE状态转为INACTIVE时）的回复消息内容，可选
        :param inactive_gc_timeout: session处于INACTIVE状态后自动回收的时间，单位秒，None为没有超时，可选

        :return: 存储session的数据的SessionObject
        """
        ...

    def get(
        self,
        scope: Scope,
        key: Hashable,
        identify: Hashable = None,
        default=None,
    ) -> SessionObject:
        """
        根据scope作用域和key，查询并获取相应的session

        :param scope: 作用域(USER, GUILD, CHANNEL, GLOBAL)
        :param key: session的键，要求为可哈希对象，根据键在作用域下查找session
        :param identify: scope作用域下的标识，不填时从栈查找本次的消息数据并自动填入（如Scope.USER会为此项自动填入user id），可选
        :param default: 未找到时返回的默认值数据，可选

        :return: 存储session的数据的SessionObject
        """
        ...

    def update(
        self,
        scope: Scope,
        key: Hashable,
        data: Dict,
        identify: Hashable = None,
    ) -> SessionObject:
        """
        根据scope作用域和key，更新相应session的存储数据，具体表现为dict.update()

        :param scope: 作用域(USER, GUILD, CHANNEL, GLOBAL)
        :param key: session的键，要求为可哈希对象，根据键在作用域下查找session
        :param data: 需要更新进入session的典类型数据
        :param identify: scope作用域下的标识，不填时从栈查找本次的消息数据并自动填入（如Scope.USER会为此项自动填入user id），可选

        :return: 存储session的数据的SessionObject
        """
        ...

    def remove(
        self, scope: Scope = None, identify: Hashable = None, key: Hashable = None
    ):
        """
        根据scope作用域和key，清空相应session的数据

        :param scope: 作用域(USER, GUILD, CHANNEL, GLOBAL)，如不存在则清空所有session
        :param identify: scope作用域下的标识，要求为可哈希对象，如不存在则清空相应scope下的所有session
        :param key: session的键，要求为可哈希对象，根据键在作用域下查找session，如不存在则清空相应identify下的所有session

        :return: 存储session的数据的SessionObject
        """
        ...

    def end(
        self, scope: Scope, key, inactive_gc_timeout: Optional[float] = 0
    ) -> SessionObject:
        """
        根据scope作用域和key，结束相应session，并在inactive_gc_timeout后进行回收

        :param scope: 作用域(USER, GUILD, CHANNEL, GLOBAL)
        :param key: session的键，要求为可哈希对象，根据键在作用域下查找session
        :param inactive_gc_timeout: session处于INACTIVE状态后自动回收的时间，单位秒，可选
        """
        ...

    def get_all(self) -> Dict:
        """
        获取所有session
        """
        ...

    def set_status(
        self,
        scope: Scope,
        key: Hashable,
        status: SessionStatus,
        identify: Hashable = None,
    ) -> None:
        """
        根据scope作用域和key，设置相应session的状态

        :param scope: 作用域(USER, GUILD, CHANNEL, GLOBAL)
        :param key: session的键，要求为可哈希对象，根据键在作用域下查找session
        :param status: session的状态，类型为SessionModel.Status
        :param identify: scope作用域下的标识，不填时从栈查找本次的消息数据并自动填入（如Scope.USER会为此项自动填入user id），可选
        """
        ...

    def get_status(
        self, scope: Scope, key: Hashable, identify: Hashable = None
    ) -> SessionStatus:
        """
        根据scope作用域和key，获取相应session的状态

        :param scope: 作用域(USER, GUILD, CHANNEL, GLOBAL)
        :param key: session的键，要求为可哈希对象，根据键在作用域下查找session
        :param identify: scope作用域下的标识，不填时从栈查找本次的消息数据并自动填入（如Scope.USER会为此项自动填入user id），可选

        :return: session的状态，类型为SessionModel.Status
        """
        ...

    # -*- fetch/commit data methods -*-
    def fetch_data(self, is_info: bool = True):
        """
        从数据库（默认为session_data文件夹）中获取session数据，更新相应session的存储数据，具体表现为dict.update()

        :param is_info: 读取成功时是否log信息，默认为True
        """
        ...

    def commit_data(self, is_info: bool = True):
        """
        将session数据保存到数据库（默认为session_data文件夹）

        :param is_info: 读取成功时是否log信息，默认为True
        """
        ...

    def set_auto_commit(self, is_auto_commit: bool):
        """
        设置是否自动保存session数据到数据库（默认为session_data文件夹）

        :param is_auto_commit: 是否自动保存session数据到数据库
        """
        ...

    def set_commit_path(self, commit_path: str):
        """
        设置保存session数据的数据库路径

        :param commit_path: 保存session数据的数据库路径
        """
        ...


class SessionPatcher(AbstractSessionManager):
    """
    Patcher for session manager, currying data from stack and pass to actual function on session manager.
    """

    def __getattribute__(self, item):
        _locals = TraceCallerData(TraceNames, ()).get_target_data()
        _session = _locals["self"].session_manager
        func = getattr(_session, item)
        if not func:
            raise AttributeError(f"Plugins.session has no attribute '{item}'")

        if item in (
            "api",
            "start",
            "register_wait_for",
            "check_wait_for",
            "del_wait_for",
            "wait_for_message_checker",
        ):
            raise AttributeError(f"Plugins.session has no attribute '{item}'")
        elif item in (
            "remove",
            "fetch_data",
            "commit_data",
            "set_auto_commit",
            "set_commit_path",
        ):
            return func

        data_obj = _locals["args"][0]

        def wrap(*args, **kwargs):
            try:
                ret = func(data_obj, *args, **kwargs)
            except Exception as e:
                _handler = stack_exception_handler(e, 2)
                _logger = _locals["self"].logger
                _logger.error(e.__repr__())
                _logger.error(_handler)
                return None
            return ret

        return wrap
