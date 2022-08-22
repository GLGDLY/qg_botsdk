# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from sys import exc_info
from traceback import extract_tb
from inspect import stack
from json import dumps
from json.decoder import JSONDecodeError
from functools import wraps
from re import split as re_split
from typing import Optional, Union, BinaryIO
from os import PathLike


def __getattr__(identifier: str) -> object:
    if re_split(r'[/\\]', stack()[1].filename)[-1] not in ('qg_bot.py', 'qg_bot_ws.py', 'api.py', 'async_api.py',
                                                           'model.py', '<frozen importlib._bootstrap>'):
        raise AssertionError("此为SDK内部使用文件，无法使用")

    return globals()[identifier.__path__]


msg_t = ('MESSAGE_CREATE', 'AT_MESSAGE_CREATE', 'DIRECT_MESSAGE_CREATE')
event_t = ('GUILD_MEMBER_ADD', 'GUILD_MEMBER_UPDATE', 'GUILD_MEMBER_REMOVE', 'MESSAGE_REACTION_ADD',
           'MESSAGE_REACTION_REMOVE', 'FORUM_THREAD_CREATE', 'FORUM_THREAD_UPDATE', 'FORUM_THREAD_DELETE',
           'FORUM_POST_CREATE', 'FORUM_POST_DELETE', 'FORUM_REPLY_CREATE', 'FORUM_REPLY_DELETE')


def template_wrapper(func):
    @wraps(func)
    def wrap(*args):
        try:
            return func(*args)
        except (JSONDecodeError, AttributeError, KeyError):
            return_ = args[0]
            code = return_.status_code if hasattr(return_, 'status_code') else getattr(return_, 'status', None)
            trace_id = getattr(return_, 'headers', None).get('X-Tps-Trace-Id')
            return objectize({'data': None, 'trace_id': trace_id, 'http_code': code, 'result': False})

    return wrap


def security_wrapper(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (JSONDecodeError, KeyError, AttributeError) as e:
            name = func.__name__
            logger = getattr(args[0], 'logger', None)
            if name == '__security_check_code':
                if logger:
                    logger.error('无法调用内容安全检测接口（备注：请检查机器人密钥是否正确）')
            else:
                if logger:
                    logger.error(f'调用内容安全检测接口失败，详情：{exception_handler(e)}')
                return False

    return wrap


def exception_handler(error):
    error_info = extract_tb(exc_info()[-1])[-1]
    return "[error:{}] File \"{}\", line {}, in {}".format(error.__repr__(), *error_info[:3])


def exception_processor(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = getattr(args[0], 'logger', None)
            if logger:
                logger.error(e.__repr__())
                logger.debug(exception_handler(e))

    return wrap


class object_class(type):
    def __repr__(self):
        return self.__doc__


class event_class(object_class):
    def reply(self, content: Optional[str] = None, image: Optional[str] = None,
              file_image: Optional[Union[bytes, BinaryIO, str, PathLike[str]]] = None,
              message_reference_id: Optional[str] = None,
              ignore_message_reference_error: Optional[bool] = None):
        """
        目前支持reply()发送被动消息的事件类型有:

        GUILD_MEMBER_ADD GUILD_MEMBER_UPDATE GUILD_MEMBER_REMOVE MESSAGE_REACTION_ADD MESSAGE_REACTION_REMOVE
        FORUM_THREAD_CREATE FORUM_THREAD_UPDATE FORUM_THREAD_DELETE FORUM_POST_CREATE FORUM_POST_DELETE
        FORUM_REPLY_CREATE FORUM_REPLY_DELETE

        剩余事件的reply()将会转为发送主动消息

        :param content: 消息文本（选填，此项与image至少需要有一个字段，否则无法下发消息）
        :param image: 图片url，不可发送本地图片（选填，此项与msg至少需要有一个字段，否则无法下发消息）
        :param file_image: 本地图片，可选三种方式传参，具体可参阅github中的example_10或帮助文档
        :param message_reference_id: 引用消息的id（选填）
        :param ignore_message_reference_error: 是否忽略获取引用消息详情错误，默认否（选填）
        :return: 返回的.data中为解析后的json数据
        """
        kwargs = locals()
        kwargs.pop('self', None)
        t = getattr(self, 't')
        if t in msg_t:
            kwargs['message_id'] = getattr(self, 'id', None)
        elif t in event_t:
            kwargs['message_id'] = getattr(self, 'event_id', None)
        if 'DIRECT_MESSAGE' in t:
            kwargs['guild_id'] = getattr(self, 'guild_id')
            return getattr(self, 'api').send_dm(**kwargs)
        else:
            kwargs['channel_id'] = getattr(self, 'channel_id') if hasattr(self, 'channel_id') \
                else getattr(self, 'id', None)
            return getattr(self, 'api').send_msg(**kwargs)


class async_event_class(object_class):
    async def reply(self, content: Optional[str] = None, image: Optional[str] = None,
                    file_image: Optional[Union[bytes, BinaryIO, str, PathLike[str]]] = None,
                    message_reference_id: Optional[str] = None,
                    ignore_message_reference_error: Optional[bool] = None):
        """
        目前支持reply()发送被动消息的事件类型有:

        GUILD_MEMBER_ADD GUILD_MEMBER_UPDATE GUILD_MEMBER_REMOVE MESSAGE_REACTION_ADD MESSAGE_REACTION_REMOVE
        FORUM_THREAD_CREATE FORUM_THREAD_UPDATE FORUM_THREAD_DELETE FORUM_POST_CREATE FORUM_POST_DELETE
        FORUM_REPLY_CREATE FORUM_REPLY_DELETE

        剩余事件的reply()将会转为发送主动消息

        :param content: 消息文本（选填，此项与image至少需要有一个字段，否则无法下发消息）
        :param image: 图片url，不可发送本地图片（选填，此项与msg至少需要有一个字段，否则无法下发消息）
        :param file_image: 本地图片，可选三种方式传参，具体可参阅github中的example_10或帮助文档
        :param message_reference_id: 引用消息的id（选填）
        :param ignore_message_reference_error: 是否忽略获取引用消息详情错误，默认否（选填）
        :return: 返回的.data中为解析后的json数据
        """
        kwargs = locals()
        kwargs.pop('self', None)
        t = getattr(self, 't')
        if t in msg_t:
            kwargs['message_id'] = getattr(self, 'id', None)
        elif t in event_t:
            kwargs['message_id'] = getattr(self, 'event_id', None)
        if 'DIRECT_MESSAGE' in t:
            kwargs['guild_id'] = getattr(self, 'guild_id')
            return getattr(self, 'api').send_dm(**kwargs)
        else:
            kwargs['channel_id'] = getattr(self, 'channel_id') if hasattr(self, 'channel_id') \
                else getattr(self, 'id', None)
            return getattr(self, 'api').send_msg(**kwargs)


def objectize(data, api=None, is_async=False):  # if api is no None, the event is a resp class
    try:
        doc = dumps(data)
    except TypeError:
        doc = str(data)
    if isinstance(data, dict):
        for keys, values in data.items():
            if keys.isnumeric():
                return data
            if isinstance(values, dict):
                data[keys] = objectize(values)
            elif isinstance(values, list):
                for i, items in enumerate(values):
                    if isinstance(items, dict):
                        data[keys][i] = objectize(items)
        data['__doc__'] = doc
        if api:
            data['api'] = api
            object_data = async_event_class('object', (object,), data) if is_async \
                else event_class('object', (object,), data)
        else:
            object_data = object_class('object', (object,), data)
        return object_data
    else:
        return data


def treat_msg(raw_msg: str):
    if not raw_msg:
        return ''
    if raw_msg[0] == '/':
        raw_msg = raw_msg[1:]
    return raw_msg.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('\xa0', ' ').strip()


@template_wrapper
def http_temp(return_, code: int):
    trace_id = return_.headers.get("X-Tps-Trace-Id")
    real_code = return_.status_code
    if real_code == code:
        return objectize({'data': None, 'trace_id': trace_id, 'http_code': real_code, 'result': True})
    else:
        return_dict = return_.json()
        return objectize({'data': return_dict, 'trace_id': trace_id, 'http_code': real_code, 'result': False})


@template_wrapper
async def async_http_temp(return_, code: int):
    trace_id = return_.headers.get("X-Tps-Trace-Id")
    real_code = return_.status
    if real_code == code:
        return objectize({'data': None, 'trace_id': trace_id, 'http_code': real_code, 'result': True})
    else:
        return_dict = await return_.json()
        return objectize({'data': return_dict, 'trace_id': trace_id, 'http_code': real_code, 'result': False})


@template_wrapper
def regular_temp(return_):
    trace_id = return_.headers.get("X-Tps-Trace-Id")
    return_dict = return_.json()
    if isinstance(return_dict, dict) and 'code' in return_dict:
        result = False
    else:
        result = True
    return objectize({'data': return_dict, 'trace_id': trace_id, 'http_code': return_.status_code, 'result': result})


@template_wrapper
async def async_regular_temp(return_):
    trace_id = return_.headers.get("X-Tps-Trace-Id")
    return_dict = await return_.json()
    if isinstance(return_dict, dict) and 'code' in return_dict:
        result = False
    else:
        result = True
    return objectize({'data': return_dict, 'trace_id': trace_id, 'http_code': return_.status, 'result': result})


@template_wrapper
def empty_temp(return_):
    trace_id = return_.headers.get("X-Tps-Trace-Id")
    return_dict = return_.json()
    if not return_dict:
        result = True
        return_dict = None
    else:
        result = False
    return objectize({'data': return_dict, 'trace_id': trace_id, 'http_code': return_.status_code, 'result': result})


@template_wrapper
async def async_empty_temp(return_):
    trace_id = return_.headers.get("X-Tps-Trace-Id")
    return_dict = await return_.json()
    if not return_dict:
        result = True
        return_dict = None
    else:
        result = False
    return objectize({'data': return_dict, 'trace_id': trace_id, 'http_code': return_.status, 'result': result})


def sdk_error_temp(message):
    return objectize({'data': {'code': -1, 'message': f'这是来自SDK的错误信息：{message}'}, 'trace_id': None,
                      'http_code': None, 'result': False})
