# !/usr/bin/env python3
# encoding: utf-8
from sys import exc_info
from traceback import extract_tb
from inspect import stack
from json import dumps
from json.decoder import JSONDecodeError
from functools import wraps
from re import split as re_split


def __getattr__(identifier: str) -> object:
    if re_split(r'[/\\]', stack()[1].filename)[-1] not in ('qg_bot.py', 'qg_bot_ws.py', 'api.py', 'async_api.py'):
        raise AssertionError("此为SDK内部使用文件，无法使用")

    return globals()[identifier.__path__]


def _template_wrapper(func):
    @wraps(func)
    def wrap(*args):
        try:
            return func(*args)
        except (JSONDecodeError, AttributeError, KeyError):
            return_ = args[0]
            code = return_.status_code if hasattr(return_, 'status_code') else getattr(return_, 'status', None)
            trace_id = return_.headers.get('X-Tps-Trace-Id', None) if hasattr(return_, 'headers') else None
            return objectize({'data': None, 'trace_id': trace_id, 'http_code': code, 'result': False})

    return wrap


def security_wrapper(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        try:
            print(func.__name__)
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
    def wrap(*args):
        try:
            return func(*args)
        except Exception as e:
            logger = getattr(args[0], 'logger', None)
            if logger:
                logger.error(e.__repr__())
                logger.debug(exception_handler(e))

    return wrap


class object_class(type):
    def __repr__(self):
        return self.__doc__


def objectize(data: dict):
    doc = dumps(data)
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
        object_data = object_class('object', (object,), data)
        return object_data
    else:
        return None


def treat_msg(raw_msg: str):
    if not raw_msg:
        return ''
    if raw_msg[0] == '/':
        raw_msg = raw_msg[1:]
    return raw_msg.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('\xa0', ' ').strip()


@_template_wrapper
def http_temp(return_, code: int):
    trace_id = return_.headers.get("X-Tps-Trace-Id", None)
    real_code = return_.status_code
    if real_code == code:
        return objectize({'data': None, 'trace_id': trace_id, 'http_code': real_code, 'result': True})
    else:
        return_dict = return_.json()
        return objectize({'data': return_dict, 'trace_id': trace_id, 'http_code': real_code, 'result': False})


@_template_wrapper
async def async_http_temp(return_, code: int):
    trace_id = return_.headers.get("X-Tps-Trace-Id", None)
    real_code = return_.status
    if real_code == code:
        return objectize({'data': None, 'trace_id': trace_id, 'http_code': real_code, 'result': True})
    else:
        return_dict = await return_.json()
        return objectize({'data': return_dict, 'trace_id': trace_id, 'http_code': real_code, 'result': False})


@_template_wrapper
def regular_temp(return_):
    trace_id = return_.headers.get("X-Tps-Trace-Id", None)
    return_dict = return_.json()
    if isinstance(return_dict, dict) and 'code' in return_dict.keys():
        result = False
    else:
        result = True
    return objectize({'data': return_dict, 'trace_id': trace_id, 'http_code': return_.status_code, 'result': result})


@_template_wrapper
async def async_regular_temp(return_):
    trace_id = return_.headers.get("X-Tps-Trace-Id", None)
    return_dict = await return_.json()
    if isinstance(return_dict, dict) and 'code' in return_dict.keys():
        result = False
    else:
        result = True
    return objectize({'data': return_dict, 'trace_id': trace_id, 'http_code': return_.status, 'result': result})


@_template_wrapper
def empty_temp(return_):
    trace_id = return_.headers.get("X-Tps-Trace-Id", None)
    return_dict = return_.json()
    if not return_dict:
        result = True
        return_dict = None
    else:
        result = False
    return objectize({'data': return_dict, 'trace_id': trace_id, 'http_code': return_.status_code, 'result': result})


@_template_wrapper
async def async_empty_temp(return_):
    trace_id = return_.headers.get("X-Tps-Trace-Id", None)
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
