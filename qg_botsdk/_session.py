#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pickle
from asyncio import AbstractEventLoop, sleep
from collections import namedtuple
from copy import deepcopy
from time import time
from typing import Dict, Hashable, Iterable, List, Optional, Union
from weakref import finalize

from ._statics import EVENTS, EventIDEvents, MsgIDEvents
from ._utils import exception_handler
from .api import API
from .api_model import BaseMessageApiModel
from .async_api import AsyncAPI
from .logger import Logger
from .model import (
    BotCommandObject,
    Model,
    Scope,
    SessionObject,
    SessionStatus,
    WaifForCommandCallback,
)

_AllScopeStr = ("USER", "GUILD", "CHANNEL", "GROUP", "GLOBAL")
ScopeRegisterKey = namedtuple("ScopeRegisterKey", _AllScopeStr)


class _SessionObject:
    def __init__(
        self,
        status: SessionStatus,
        data: Dict,
        timeout: Optional[float] = None,
        last_operate: float = 0,
        timeout_reply: str = None,
        inactive_gc_timeout: Optional[float] = None,
        gc_timeout_stamp: Optional[float] = None,
        timeout_reply_api: Optional[str] = None,
        timeout_reply_params: Dict = None,
        timeout_reply_message_id_expire: float = None,
    ):
        self.status = status
        self.data = data
        self.timeout = timeout
        self.last_operate = last_operate
        self.timeout_reply = timeout_reply
        self.inactive_gc_timeout = inactive_gc_timeout  # 处于INACTIVE的session在相隔这段时间后被回收
        self.gc_timeout_stamp = gc_timeout_stamp  # 处于INACTIVE的session在此时间后被回收
        self.timeout_reply_api = timeout_reply_api  # 超时回复的消息API
        self.timeout_reply_params = timeout_reply_params  # 超时回复的消息默认参数
        self.timeout_reply_message_id_expire = (
            timeout_reply_message_id_expire  # 超时回复的消息ID过期时间
        )

    def __repr__(self):
        return (
            f"<SessionObject status={self.status} data={self.data} timeout={self.timeout} "
            f"last_operate={self.last_operate} timeout_reply={self.timeout_reply} "
            f"inactive_gc_timeout={self.inactive_gc_timeout} gc_timeout_stamp={self.gc_timeout_stamp} "
            f"timeout_reply_params={self.timeout_reply_params} "
            f"timeout_reply_message_id_expire={self.timeout_reply_message_id_expire}>"
        )


class SessionManager:
    """
    Implementation of Session Manager, used to create and manage sessions with user, guild, channel and global scope.
    Life cycle of session: ACTIVE --(timeout || active end)--> INACTIVE --(inactive_gc_timeout)--> GC

    Structure of sessions:
        - normal sessions(e.g. user) : {"user_id": {"key": _SessionObject, ...}, ...}
        - global sessions struct: {"key": _SessionObject, ...}
    """

    def __init__(
        self,
        logger: Logger,
        commit_path: Optional[str] = None,
        is_auto_commit: bool = True,
    ):
        self.__sessions: Dict = {x: {} for x in _AllScopeStr}
        self.__sessions_pk_cache = None
        self.__wait_for_registers: Dict = {}
        self.__logger: Logger = logger
        self.__bot_identify: str = logger.bot_app_id
        self.__commit_path: str = commit_path or os.path.join(
            os.getcwd(), "session_data"
        )
        self.__check_path(self.__commit_path)
        self.__is_auto_commit = is_auto_commit
        self.__is_running = False
        self.fetch_data()
        self.api = None  # what a cursed implementation...
        self.__finalizer = finalize(
            self, lambda x: x(), self.__del__
        )  # ensure commit_data() is called before exit

    def __logger_exception_handler(self, attr: str, msg: str):
        try:
            getattr(self.__logger, attr, print)(msg)
        except Exception:
            print(msg)

    def __del__(self):
        if self.__is_auto_commit:
            self.__logger_exception_handler("info", "Session Manager结束中，正在保存数据...")
            try:
                self.commit_data(is_info=False)
            except Exception as e:
                self.__logger_exception_handler(
                    "error", f"Session Manager保存数据时出现错误：{e.__repr__()}"
                )

    # -*- class internal methods -*-
    @staticmethod
    def __check_path(commit_path: str):
        if not os.path.exists(commit_path):
            path_splits = os.path.split(commit_path)
            if "." in path_splits[-1]:
                raise ValueError(f"路径 '{commit_path}' 不是文件夹（包含'.'）")
            os.makedirs(commit_path)
        elif not os.path.isdir(commit_path):
            raise ValueError(f"路径 '{commit_path}' 不是文件夹")

    @staticmethod
    def __end_session(session: _SessionObject):
        session.status = SessionStatus.INACTIVE
        gc_timeout = session.inactive_gc_timeout
        session.gc_timeout_stamp = (
            time() + gc_timeout if gc_timeout is not None else None
        )

    @staticmethod
    def __update_last_op(session: _SessionObject):
        session.last_operate = time()
        if session.status != SessionStatus.ACTIVE:
            session.status = SessionStatus.ACTIVE

    def __manage_session_object(self, loop, time_now, session, scope, identify):
        _change = False
        gc_keys = []
        for k, v in session.items():
            if not isinstance(
                v, _SessionObject
            ):  # prevent dead loop on non valid object
                gc_keys.append(k)
                continue
            if (
                v.status == SessionStatus.ACTIVE
                and v.timeout is not None
                and time_now - v.last_operate > v.timeout
            ):
                if v.timeout_reply:
                    try:
                        if time_now > v.timeout_reply_message_id_expire:
                            del v.timeout_reply_params["message_id"]
                        elif (
                            v.timeout_reply_api == "send_group_msg"
                            or v.timeout_reply_api == "send_qq_dm"
                        ):
                            v.timeout_reply_params[
                                "msg_seq"
                            ] = 999999999  # 保证消息不会因为这破msg_seq而被忽略
                        _params = {"content": v.timeout_reply, **v.timeout_reply_params}
                        if isinstance(self.api, AsyncAPI):
                            loop.create_task(
                                getattr(self.api, v.timeout_reply_api)(**_params)
                            )
                        elif isinstance(self.api, API):
                            loop.create_task(
                                getattr(self.api._api, v.timeout_reply_api)(**_params)
                            )
                    except Exception as e:
                        self.__logger.error(
                            f"Session({scope}::{k}) 超时回调错误：{e.__repr__()}"
                        )
                        self.__logger.error(exception_handler(e))
                if identify:
                    self.__logger.info(f"Session({scope}::{identify}::{k}) 已超时")
                else:
                    self.__logger.info(f"Session({scope}::{k}) 已超时")
                self.__end_session(v)
                _change = True
            if (
                v.status == SessionStatus.INACTIVE
                and v.gc_timeout_stamp is not None
                and time_now > v.gc_timeout_stamp
            ):
                gc_keys.append(k)
        for k in gc_keys:
            del session[k]
            _change = True
        return _change

    async def __manager_loop(self, loop: AbstractEventLoop):
        while True:
            await sleep(0.5)
            change = False
            try:
                time_now = time()
                for scope in _AllScopeStr:
                    sessions = self.__check_scope(scope)
                    if scope == "GLOBAL":
                        change = self.__manage_session_object(
                            loop, time_now, sessions, scope, None
                        )
                    else:
                        gc_identifies = []
                        for identify, session in sessions.items():
                            change = self.__manage_session_object(
                                loop, time_now, session, scope, identify
                            )
                            if not session:
                                gc_identifies.append(identify)
                        for identify in gc_identifies:
                            del sessions[identify]
                            change = True
            except Exception as e:
                self.__logger.error(e.__repr__())
                self.__logger.error(exception_handler(e))
            if self.__is_auto_commit:
                if change:
                    self.commit_data(is_info=False)
                else:
                    _new_pk_data = pickle.dumps(self.__sessions)
                    if self.__sessions_pk_cache != _new_pk_data:
                        self.__sessions_pk_cache = _new_pk_data
                        self.commit_data(is_info=False, pk_data=_new_pk_data)

    @staticmethod
    def __valid_scope(scope):
        if isinstance(scope, Scope):
            scope = scope.value
        elif scope in _AllScopeStr:
            pass
        else:
            raise ValueError("scope参数仅接受user, guild, channel, global")
        return scope

    def __check_identify(self, scope: Union[Scope, str], data) -> Hashable:
        if scope == Scope.USER or scope == "USER":
            identify = self.__get_author_id(data)
        elif scope == Scope.GUILD or scope == "GUILD":
            identify = self.__get_guild_id(data)
        elif scope == Scope.CHANNEL or scope == "CHANNEL":
            identify = self.__get_channel_id(data)
        elif scope == Scope.GROUP or scope == "GROUP":
            identify = self.__get_group_openid(data)
        else:
            identify = None
        return identify

    def __get_reply_params(self, data) -> Dict:
        timeout_reply_api = None
        timeout_reply_params = {}

        try:
            t = data.t
            if t in MsgIDEvents:
                timeout_reply_params = {"message_id": getattr(data, "id", None)}
            elif t in EventIDEvents:
                timeout_reply_params = {"message_id": getattr(data, "event_id", None)}

            if (
                t in EVENTS.MESSAGE_CREATE
                or t in EVENTS.REACTION
                or t in EVENTS.INTERACTION
                or t in EVENTS.AUDIT
                or t in EVENTS.AUDIO
                or t in EVENTS.ALC_MEMBER
            ):
                timeout_reply_params["channel_id"] = data.channel_id
                timeout_reply_api = "send_msg"
            elif t in EVENTS.DM_CREATE:
                timeout_reply_params["guild_id"] = data.guild_id
                timeout_reply_api = "send_dm"
            elif t in EVENTS.GROUP_AT_MESSAGE_CREATE or t in EVENTS.GROUP:
                timeout_reply_params["group_openid"] = data.group_openid
                timeout_reply_api = "send_group_msg"
            elif t in EVENTS.C2C_MESSAGE_CREATE:
                timeout_reply_params["user_openid"] = data.author.user_openid
                timeout_reply_api = "send_qq_dm"
            elif t in EVENTS.MESSAGE_DELETE:
                if t in t in ("MESSAGE_DELETE", "PUBLIC_MESSAGE_DELETE"):
                    timeout_reply_params["channel_id"] = data.message.channel_id
                    timeout_reply_api = "send_msg"
                else:  # DIRECT_MESSAGE_DELETE
                    timeout_reply_params["guild_id"] = data.message.guild_id
                    timeout_reply_api = "send_dm"
            elif t in EVENTS.CHANNEL:
                timeout_reply_params["channel_id"] = data.id
                timeout_reply_api = "send_msg"
            elif t in EVENTS.FRIEND:
                timeout_reply_params["user_openid"] = data.openid
                timeout_reply_api = "send_qq_dm"
            # not support event: FORUM, GUILD, GUILD_MEMBER, OPEN_FORUM
        except Exception as e:
            self.__logger.error(f"Session Manager 获取回复参数时出现错误：{e.__repr__()}")
            self.__logger.error(exception_handler(e))

        return {
            "timeout_reply_api": timeout_reply_api,
            "timeout_reply_params": timeout_reply_params,
        }

    def __check_scope(
        self, scope: Union[Scope, str]
    ) -> Dict[Hashable, Dict[Hashable, _SessionObject]]:
        if scope == Scope.USER or scope == "USER":
            target_sessions = self.__sessions["USER"]
        elif scope == Scope.GUILD or scope == "GUILD":
            target_sessions = self.__sessions["GUILD"]
        elif scope == Scope.CHANNEL or scope == "CHANNEL":
            target_sessions = self.__sessions["CHANNEL"]
        elif scope == Scope.GROUP or scope == "GROUP":
            target_sessions = self.__sessions["GROUP"]
        else:
            target_sessions = self.__sessions["GLOBAL"]
        return target_sessions

    @staticmethod
    def __get_author_id(data) -> Hashable:
        t = data.t
        if t in EVENTS.MESSAGE_CREATE or t in EVENTS.DM_CREATE:
            return data.author.id
        elif t in EVENTS.GROUP_AT_MESSAGE_CREATE:
            return data.author.member_openid
        elif t in EVENTS.C2C_MESSAGE_CREATE:
            return data.author.user_openid
        elif t in EVENTS.GROUP:
            return data.group_openid
        elif t in EVENTS.FRIEND:
            return data.openid
        elif t in EVENTS.GUILD or t in EVENTS.CHANNEL:
            return data.op_user_id
        elif t in EVENTS.GUILD_MEMBER:
            return data.user.id
        elif t in EVENTS.MESSAGE_DELETE:
            return data.op_user.id
        elif t in EVENTS.FORUM or t in EVENTS.OPEN_FORUM:
            return data.author_id
        elif t in EVENTS.REACTION or t in EVENTS.ALC_MEMBER:
            return data.user_id
        elif t in EVENTS.INTERACTION:
            return data.data.resolved.user_id
        return 0

    @staticmethod
    def __get_guild_id(data) -> Hashable:
        t = data.t
        if (
            t in EVENTS.MESSAGE_CREATE
            or t in EVENTS.DM_CREATE
            or t in EVENTS.CHANNEL
            or t in EVENTS.GUILD_MEMBER
            or t in EVENTS.AUDIT
            or t in EVENTS.FORUM
            or t in EVENTS.OPEN_FORUM
            or t in EVENTS.AUDIO
            or t in EVENTS.REACTION
            or t in EVENTS.INTERACTION
            or t in EVENTS.ALC_MEMBER
        ):
            return data.guild_id
        elif t in EVENTS.GUILD:
            return data.id
        elif t in EVENTS.MESSAGE_DELETE:
            return data.message.guild_id
        return 0

    @staticmethod
    def __get_channel_id(data) -> Hashable:
        t = data.t
        if (
            t in EVENTS.MESSAGE_CREATE
            or t in EVENTS.DM_CREATE
            or t in EVENTS.FORUM
            or t in EVENTS.OPEN_FORUM
            or t in EVENTS.AUDIO
            or t in EVENTS.REACTION
            or t in EVENTS.INTERACTION
            or t in EVENTS.ALC_MEMBER
        ):
            return data.channel_id
        elif t in EVENTS.CHANNEL:
            return data.id
        elif t in EVENTS.MESSAGE_DELETE:
            return data.message.channel_id
        return 0

    @staticmethod
    def __get_group_openid(data) -> Hashable:
        t = data.t
        if t in EVENTS.GROUP_AT_MESSAGE_CREATE:
            return data.group_openid
        elif t in EVENTS.GROUP:
            return data.id
        return 0

    def __check_and_get_target_session(self, obj, scope, key, identify):
        if not identify:
            identify = self.__check_identify(scope, obj)
        scope = self.__valid_scope(scope)
        target_sessions = self.__check_scope(scope)
        if identify:
            if identify not in target_sessions or key not in target_sessions[identify]:
                raise KeyError(f"Scope {scope} 中不存在 {identify}::{key} 的session")
            target_session = target_sessions[identify][key]
        else:
            if key not in target_sessions:
                raise KeyError(f"Scope {scope} 中不存在 {key} 的session")
            target_session = target_sessions[key]
        return target_session

    # -*- user methods -*-
    def new(
        self,
        obj,
        scope: Scope,
        key: Hashable,
        data: Dict = None,
        identify: Hashable = None,
        is_replace: bool = True,
        timeout: Optional[float] = None,
        timeout_reply: Optional[Union[str, BaseMessageApiModel]] = None,
        inactive_gc_timeout: Optional[float] = 0,
    ) -> SessionObject:
        if not identify:
            identify = self.__check_identify(scope, obj)
        scope = self.__valid_scope(scope)
        target_sessions = self.__check_scope(scope)
        if identify:
            if identify not in target_sessions:
                target_sessions[identify] = {}
            target_sessions = target_sessions[identify]
        if key in target_sessions and not is_replace:
            if identify:
                raise KeyError(f"Scope {scope} 中已存在 {identify}::{key} 的session")
            else:
                raise KeyError(f"Scope {scope} 中已存在 {key} 的session")
        target_sessions[key] = _SessionObject(
            status=SessionStatus.ACTIVE,
            data=data if data is not None else {},
            timeout=timeout,
            last_operate=time(),
            timeout_reply=timeout_reply,
            inactive_gc_timeout=inactive_gc_timeout,
            timeout_reply_message_id_expire=time() + 300,
            **self.__get_reply_params(obj),
        )
        if self.__is_auto_commit:
            self.commit_data(is_info=False)
        return SessionObject(scope, SessionStatus.ACTIVE, key, data, identify)

    def get(
        self,
        obj,
        scope: Scope,
        key: Hashable,
        identify: Hashable = None,
        default=None,
    ) -> SessionObject:
        if not identify:
            identify = self.__check_identify(scope, obj)
        scope = self.__valid_scope(scope)
        target_sessions = self.__check_scope(scope)
        if identify:
            if identify not in target_sessions or key not in target_sessions[identify]:
                return default
            target_session = target_sessions[identify][key]
        else:
            if key not in target_sessions:
                return default
            target_session = target_sessions[key]
        self.__update_last_op(target_session)
        return SessionObject(
            scope, target_session.status, key, target_session.data, identify
        )

    def update(
        self,
        obj,
        scope: Scope,
        key: Hashable,
        data: Dict,
        identify: Hashable = None,
    ) -> SessionObject:
        target_session = self.__check_and_get_target_session(obj, scope, key, identify)
        target_session.data.update(data)
        self.__update_last_op(target_session)
        if self.__is_auto_commit:
            self.commit_data(is_info=False)
        return SessionObject(
            scope, target_session.status, key, target_session.data, identify
        )

    def remove(
        self, scope: Scope = None, identify: Hashable = None, key: Hashable = None
    ):
        if not scope:
            self.__sessions = {x: {} for x in _AllScopeStr}
            return
        scope = self.__valid_scope(scope)
        target_sessions = self.__check_scope(scope)
        if not key and not identify:
            target_sessions.clear()
            if self.__is_auto_commit:
                self.commit_data(is_info=False)
            return
        if not key and identify:
            target_sessions[identify] = {}
            if self.__is_auto_commit:
                self.commit_data(is_info=False)
            return
        if identify:
            if identify not in target_sessions or key not in target_sessions[identify]:
                raise KeyError(f"Scope {scope} 中不存在 {identify}::{key} 的session")
            target_sessions = target_sessions[identify]
        else:
            if key not in target_sessions:
                raise KeyError(f"Scope {scope} 中不存在 {key} 的session")
        target_sessions.pop(key)
        if self.__is_auto_commit:
            self.commit_data(is_info=False)

    def end(
        self,
        obj,
        scope: Scope,
        key: Hashable,
        identify: Hashable = None,
        inactive_gc_timeout: Optional[float] = 0,
    ) -> SessionObject:
        target_session = self.__check_and_get_target_session(obj, scope, key, identify)
        target_session.inactive_gc_timeout = inactive_gc_timeout
        self.__end_session(target_session)
        if self.__is_auto_commit:
            self.commit_data(is_info=False)
        return SessionObject(
            scope, target_session.status, key, target_session.data, identify
        )

    def get_all(self) -> Dict:
        return deepcopy(self.__sessions)

    def set_status(
        self,
        obj,
        scope: Scope,
        key: Hashable,
        status: SessionStatus,
        identify: Hashable = None,
    ):
        if not isinstance(status, SessionStatus):
            raise ValueError("status 必须是 SessionStatus 的枚举值")
        if status == SessionStatus.INACTIVE:
            self.end(obj, scope, key, identify)
            return
        target_session = self.__check_and_get_target_session(obj, scope, key, identify)
        target_session.status = status
        target_session.last_operate = time()
        if self.__is_auto_commit:
            self.commit_data(is_info=False)

    def get_status(
        self, obj, scope: Scope, key: Hashable, identify: Hashable = None
    ) -> SessionStatus:
        target_session = self.__check_and_get_target_session(obj, scope, key, identify)
        return target_session.status

    # -*- fetch/commit data methods -*-
    def fetch_data(self, is_info: bool = True):
        _path = os.path.join(self.__commit_path, f"session_{self.__bot_identify}.db")
        if not os.path.exists(_path):
            return
        try:
            with open(_path, "rb") as f_db:
                db = pickle.loads(f_db.read())
                for scope in _AllScopeStr:
                    try:
                        scope_data = db[scope]
                    except KeyError:
                        continue
                    except Exception as e:
                        self.__logger.error(
                            f"Session Manager 读取 Scope::{scope} 数据时出现错误，将跳过：{repr(e)}"
                        )
                    if scope == "GLOBAL":
                        for k in scope_data:
                            try:
                                self.__sessions[scope][k] = scope_data[k]
                            except Exception as e:
                                self.__logger.error(
                                    f"Session Manager 读取 Scope::{scope}::{k} 数据时出现错误，将跳过：{repr(e)}"
                                )
                    else:
                        for _id in scope_data:
                            if _id not in self.__sessions[scope]:
                                self.__sessions[scope][_id] = {}
                            for k in scope_data[_id]:
                                try:
                                    self.__sessions[scope][_id][k] = scope_data[_id][k]
                                except Exception as e:
                                    self.__logger.error(
                                        f"Session Manager 读取 Scope::{scope}::{_id}::{k} 数据时出现错误，将跳过：{repr(e)}"
                                    )
            if is_info:
                self.__logger.info(f"Session Manager 读取了 {self.__commit_path} 的数据")
        except Exception as e:
            self.__logger.error(f"Session Manager 读取 {_path} 时出现错误，将跳过：{repr(e)}")

    def commit_data(self, is_info: bool = True, pk_data: Optional[bytes] = None):
        _path = os.path.join(self.__commit_path, f"session_{self.__bot_identify}.db")
        try:
            with open(_path, "wb") as f_db:
                if not pk_data:
                    pk_data = pickle.dumps(self.__sessions)
                f_db.write(pk_data)
            if is_info:
                self.__logger.info(f"Session Manager 写入了 {_path} 的数据")
        except Exception as e:
            self.__logger.error(f"Session Manager 写入 {_path} 时出现错误，将跳过：{repr(e)}")

    def set_auto_commit(self, is_auto_commit: bool):
        self.__is_auto_commit = is_auto_commit

    def set_commit_path(self, commit_path: str):
        self.__check_path(commit_path)
        self.__commit_path = commit_path

    # -*- helper private methods for internal use -*-
    def start(self, loop: AbstractEventLoop):
        if not self.__is_running:
            loop.create_task(self.__manager_loop(loop))
            self.__is_running = True

    # -*- helper private methods for api.wait_for -*-
    def register_wait_for(
        self, obj, scopes: Union[Scope, Iterable[Scope]], command: BotCommandObject
    ):
        _scope_value = {x: None for x in _AllScopeStr}
        if isinstance(scopes, Iterable):
            for scope in scopes:
                if not isinstance(scope, Scope):
                    raise ValueError("scope 必须是 Scope 的枚举值")
                _scope_value[scope.value] = self.__check_identify(scope, obj)
        else:
            if not isinstance(scopes, Scope):
                raise ValueError("scope 必须是 Scope 的枚举值")
            _scope_value[scopes.value] = self.__check_identify(scopes, obj)
        _scope_key = ScopeRegisterKey(**_scope_value)
        if _scope_key not in self.__wait_for_registers:
            self.__wait_for_registers[_scope_key] = {}
        self.__wait_for_registers[_scope_key][command] = None
        return _scope_key

    def check_wait_for(self, scope_key: ScopeRegisterKey, command: BotCommandObject):
        if (
            scope_key not in self.__wait_for_registers
            or command not in self.__wait_for_registers[scope_key]
        ):
            return False, None
        data = self.__wait_for_registers[scope_key][command]
        if data:
            del self.__wait_for_registers[scope_key][command]
            if not self.__wait_for_registers[scope_key]:
                del self.__wait_for_registers[scope_key]
        return True, data

    def del_wait_for(self, scope_key: ScopeRegisterKey, command: BotCommandObject):
        if scope_key not in self.__wait_for_registers:
            return
        if command in self.__wait_for_registers[scope_key]:
            del self.__wait_for_registers[scope_key][command]
        if not self.__wait_for_registers[scope_key]:
            del self.__wait_for_registers[scope_key]

    def wait_for_message_checker(
        self, obj: Model.MESSAGE
    ) -> List[WaifForCommandCallback]:
        triggered_commands = []
        _scope_value = {
            scope: self.__check_identify(scope, obj) for scope in _AllScopeStr
        }
        for scope_key, command_callback in self.__wait_for_registers.items():
            flag = True
            for scope in _AllScopeStr:
                scope_key_value = getattr(scope_key, scope)
                if (
                    scope_key_value is not None
                    and scope_key_value != _scope_value[scope]
                ):
                    flag = False
                    break
            if flag:
                for command in command_callback:
                    triggered_commands.append(
                        WaifForCommandCallback(
                            command=command,
                            callback=lambda data: command_callback.__setitem__(
                                command, data
                            ),
                        )
                    )
        return triggered_commands
