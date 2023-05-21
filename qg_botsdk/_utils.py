#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from asyncio import iscoroutinefunction
from copy import deepcopy
from functools import wraps
from inspect import Signature, signature, stack
from json import dumps, loads
from json.decoder import JSONDecodeError
from sys import exc_info
from time import localtime, strftime
from traceback import extract_tb
from typing import BinaryIO, Callable, Iterable, Optional, Union

from aiohttp import ContentTypeError

from .version import __version__

general_header = {"User-Agent": f"qg-botsdk v{__version__}"}
security_header = {
    "Content-Type": "application/json",
    "charset": "UTF-8",
    "User-Agent": f"qg-botsdk v{__version__}",
}
retry_err_code = (
    101,
    11281,
    11252,
    11263,
    11242,
    11252,
    130000,
    306003,
    306005,
    306006,
    501002,
    501003,
    501004,
    501006,
    501007,
    501011,
    501012,
    620007,
)
msg_t = ("MESSAGE_CREATE", "AT_MESSAGE_CREATE", "DIRECT_MESSAGE_CREATE")
event_t = (
    "GUILD_MEMBER_ADD",
    "GUILD_MEMBER_UPDATE",
    "GUILD_MEMBER_REMOVE",
    "MESSAGE_REACTION_ADD",
    "MESSAGE_REACTION_REMOVE",
    "FORUM_THREAD_CREATE",
    "FORUM_THREAD_UPDATE",
    "FORUM_THREAD_DELETE",
    "FORUM_POST_CREATE",
    "FORUM_POST_DELETE",
    "FORUM_REPLY_CREATE",
    "FORUM_REPLY_DELETE",
    "INTERACTION_CREATE",
)


def template_wrapper(func):
    @wraps(func)
    async def wrap(*args):
        try:
            result = await func(*args)
            return result
        except (JSONDecodeError, ContentTypeError, AttributeError, KeyError):
            return_ = args[0]
            code = (
                return_.status_code
                if hasattr(return_, "status_code")
                else getattr(return_, "status", None)
            )
            trace_id = getattr(return_, "headers", {}).get("X-Tps-Trace-Id")
            return objectize(
                {"data": None, "trace_id": trace_id, "http_code": code, "result": False}
            )

    return wrap


def security_wrapper(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (JSONDecodeError, KeyError, AttributeError) as e:
            name = func.__name__
            logger = getattr(args[0], "logger", None)
            if name == "__security_check_code":
                if logger:
                    logger.error("无法调用内容安全检测接口（备注：请检查机器人密钥是否正确）")
            else:
                if logger:
                    logger.error(f"调用内容安全检测接口失败，详情：{exception_handler(e)}")
                return False

    return wrap


def stack_exception_handler(error, stack_no: int = 1):
    target_frame = stack()[stack_no]
    return '[error:{}] File "{}", line {}, in {}'.format(
        error.__repr__(),
        target_frame.filename,
        target_frame.lineno,
        target_frame.function,
    )


def exception_handler(error):
    error_info = extract_tb(exc_info()[-1])[-1]
    return '[error:{}] File "{}", line {}, in {}'.format(
        error.__repr__(), *error_info[:3]
    )


def exception_processor(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = getattr(args[0], "logger", None)
            if logger:
                logger.error(e.__repr__())
                logger.error(exception_handler(e))
            else:
                t = strftime("%m-%d %H:%M:%S", localtime())
                print(f"\033[1;31m[{t}] [ERROR]\033[0m {e.__repr__()}")
                print(f"[{t}] [ERROR] {exception_handler(e)}")

    return wrap


class object_class:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def __getattribute__(self, item):
        if item == "__doc__":
            return object.__getattribute__(self, "__repr__")()
        return object.__getattribute__(self, item)

    def __repr__(self):
        try:
            return dumps(self._data)
        except (TypeError, ValueError):
            return str(self._data)

    @property
    def dict(self):
        return self._data


def _send_msg():  # Cannot direct import from _api_model.py since circular import
    class SendMsg(object_class):
        class data:
            id: str
            channel_id: str
            guild_id: str
            content: str
            timestamp: str
            tts: bool
            mention_everyone: bool
            author: dict
            pinned: bool
            type: int
            flags: int
            seq_in_channel: str
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return SendMsg


_reply_args = (
    "content",
    "image",
    "file_image",
    "message_reference_id",
    "ignore_message_reference_error",
)


class event_class(object_class):
    def reply(
        self,
        content: Optional[str] = None,
        image: Optional[str] = None,
        file_image: Optional[Union[bytes, BinaryIO, str]] = None,
        message_reference_id: Optional[str] = None,
        ignore_message_reference_error: Optional[bool] = None,
    ) -> _send_msg():
        """
        目前支持reply()发送被动消息的事件类型有:

        GUILD_MEMBER_ADD GUILD_MEMBER_UPDATE GUILD_MEMBER_REMOVE MESSAGE_REACTION_ADD MESSAGE_REACTION_REMOVE
        FORUM_THREAD_CREATE FORUM_THREAD_UPDATE FORUM_THREAD_DELETE FORUM_POST_CREATE FORUM_POST_DELETE
        FORUM_REPLY_CREATE FORUM_REPLY_DELETE INTERACTION_CREATE

        剩余事件的reply()将会转为发送主动消息

        :param content: 消息文本（选填，此项与image至少需要有一个字段，否则无法下发消息）
        :param image: 图片url，不可发送本地图片（选填，此项与msg至少需要有一个字段，否则无法下发消息）
        :param file_image: 本地图片，可选三种方式传参，具体可参阅github中的example_10或帮助文档
        :param message_reference_id: 引用消息的id（选填）
        :param ignore_message_reference_error: 是否忽略获取引用消息详情错误，默认否（选填）
        :return: 返回的.data中为解析后的json数据
        """
        raw_args = locals()
        kwargs = {arg: raw_args[arg] for arg in _reply_args}
        t = getattr(self, "t", None)
        if t in msg_t:
            kwargs["message_id"] = getattr(self, "id", None)
        elif t in event_t:
            kwargs["message_id"] = getattr(self, "event_id", None)
        if "DIRECT_MESSAGE" in t:
            kwargs["guild_id"] = getattr(self, "guild_id", None)
            return getattr(self, "api").send_dm(**kwargs)
        else:
            kwargs["channel_id"] = (
                self.channel_id
                if hasattr(self, "channel_id")
                else getattr(self, "id", None)
            )
            return getattr(self, "api").send_msg(**kwargs)


class async_event_class(object_class):
    async def reply(
        self,
        content: Optional[str] = None,
        image: Optional[str] = None,
        file_image: Optional[Union[bytes, BinaryIO, str]] = None,
        message_reference_id: Optional[str] = None,
        ignore_message_reference_error: Optional[bool] = None,
    ) -> _send_msg():
        """
        目前支持reply()发送被动消息的事件类型有:

        GUILD_MEMBER_ADD GUILD_MEMBER_UPDATE GUILD_MEMBER_REMOVE MESSAGE_REACTION_ADD MESSAGE_REACTION_REMOVE
        FORUM_THREAD_CREATE FORUM_THREAD_UPDATE FORUM_THREAD_DELETE FORUM_POST_CREATE FORUM_POST_DELETE
        FORUM_REPLY_CREATE FORUM_REPLY_DELETE INTERACTION_CREATE

        剩余事件的reply()将会转为发送主动消息

        :param content: 消息文本（选填，此项与image至少需要有一个字段，否则无法下发消息）
        :param image: 图片url，不可发送本地图片（选填，此项与msg至少需要有一个字段，否则无法下发消息）
        :param file_image: 本地图片，可选三种方式传参，具体可参阅github中的example_10或帮助文档
        :param message_reference_id: 引用消息的id（选填）
        :param ignore_message_reference_error: 是否忽略获取引用消息详情错误，默认否（选填）
        :return: 返回的.data中为解析后的json数据
        """
        raw_args = locals()
        kwargs = {arg: raw_args[arg] for arg in _reply_args}
        t = getattr(self, "t", None)
        if t in msg_t:
            kwargs["message_id"] = getattr(self, "id", None)
        elif t in event_t:
            kwargs["message_id"] = getattr(self, "event_id", None)
        if "DIRECT_MESSAGE" in t:
            kwargs["guild_id"] = getattr(self, "guild_id", None)
            return await getattr(self, "api").send_dm(**kwargs)
        else:
            kwargs["channel_id"] = (
                self.channel_id
                if hasattr(self, "channel_id")
                else getattr(self, "id", None)
            )
            return await getattr(self, "api").send_msg(**kwargs)


def objectize(
    data, api=None, is_async=False, is_recursion=False
):  # if api is not None, the event is a resp class
    if isinstance(data, dict):
        _data = data
        if not is_recursion:
            # create a copy that doesn't reference to the original data
            data = deepcopy(data)
        # main func to process data
        for keys, values in data.items():
            if keys.isnumeric():
                return data
            if isinstance(values, dict):
                data[keys] = objectize(values, is_recursion=True)
            elif isinstance(values, list):
                for i, items in enumerate(values):
                    if isinstance(items, dict):
                        data[keys][i] = objectize(items, is_recursion=True)
        data["_data"] = _data
        if api:
            data["api"] = api
            object_data = async_event_class(**data) if is_async else event_class(**data)
        else:
            object_data = object_class(**data)
        return object_data
    else:
        return data


def treat_msg(raw_msg: str, at: str):
    raw_msg = raw_msg if raw_msg.find(at) else raw_msg.replace(at, "", 1).strip()
    if not raw_msg:
        return ""
    if raw_msg[0] == "/":
        raw_msg = raw_msg[1:]
    return (
        raw_msg.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("\xa0", " ")
        .strip()
    )


def treat_thread(data: dict):
    for items in ("content", "title"):
        try:
            data["d"]["thread_info"][items] = loads(
                data.get("d", {}).get("thread_info", {}).get(items, "{}")
            )
        except JSONDecodeError:
            pass


@template_wrapper
async def http_temp(return_, code: int):
    trace_id = return_.headers.get("X-Tps-Trace-Id")
    real_code = return_.status
    if real_code == code:
        return objectize(
            {"data": None, "trace_id": trace_id, "http_code": real_code, "result": True}
        )
    else:
        return_dict = await return_.json()
        return objectize(
            {
                "data": return_dict,
                "trace_id": trace_id,
                "http_code": real_code,
                "result": False,
            }
        )


@template_wrapper
async def regular_temp(return_):
    trace_id = return_.headers.get("X-Tps-Trace-Id")
    return_dict = await return_.json()
    if isinstance(return_dict, dict) and "code" in return_dict:
        result = False
    else:
        result = True
    return objectize(
        {
            "data": return_dict,
            "trace_id": trace_id,
            "http_code": return_.status,
            "result": result,
        }
    )


@template_wrapper
async def empty_temp(return_):
    trace_id = return_.headers.get("X-Tps-Trace-Id")
    return_dict = await return_.json()
    if not return_dict:
        result = True
        return_dict = None
    else:
        result = False
    return objectize(
        {
            "data": return_dict,
            "trace_id": trace_id,
            "http_code": return_.status,
            "result": result,
        }
    )


def sdk_error_temp(message):
    return objectize(
        {
            "data": {"code": -1, "message": f"这是来自SDK的错误信息：{message}"},
            "trace_id": None,
            "http_code": None,
            "result": False,
        }
    )


def func_type_checker(func, *args, is_async: bool = False):
    sig = signature(func).parameters
    sig_keys = list(sig.keys())
    sig_keys_len = len(sig_keys)
    if sig_keys_len != len(args):
        raise TypeError(
            f'函数{func.__name__}应包含以下类型的{len(args)}个参数：{" ".join(args)}\n'
            f"当前为{sig_keys_len}个参数：{sig_keys}"
        )
    for i in range(sig_keys_len):
        annotation = sig[sig_keys[i]].annotation
        if annotation is not Signature.empty and annotation != args[i]:
            raise TypeError(f"函数{func.__name__}中{sig_keys[i]}参数应为类型：{args[i]}")
    if is_async:
        if not iscoroutinefunction(func):
            raise TypeError(f"函数{func.__name__}应为一个async coroutine函数")
    else:
        if not isinstance(func, Callable) or iscoroutinefunction(func):
            raise TypeError(f"函数{func.__name__}应为一个普通函数")


class TraceCallerData:
    def __init__(self, caller_names: Iterable[str], datas: Iterable[str]):
        self.caller_names = caller_names
        self.datas = datas

    def get_target_data(self):
        for frame in stack():
            caller_name = frame.function
            if caller_name in self.caller_names:
                if not self.datas:
                    return frame.frame.f_locals
                try:
                    target_data = frame.frame.f_locals
                    for data in self.datas:
                        target_data = (
                            target_data.get(data, None)
                            if isinstance(target_data, dict)
                            else getattr(target_data, data, None)
                        )
                    return target_data
                except Exception:
                    pass

    def __getattr__(self, item):
        target_data = self.get_target_data()
        if target_data:
            return getattr(target_data, item)
        raise AttributeError(
            f"没有追溯到 {'::'.join(self.datas)} 变量（probably because of haven't start bot instance）"
        )

    def __getitem__(self, item):
        target_data = self.get_target_data()
        if target_data:
            return target_data[item]
        raise KeyError(
            f"没有追溯到 {'::'.join(self.datas)} 变量（probably because of haven't start bot instance）"
        )
