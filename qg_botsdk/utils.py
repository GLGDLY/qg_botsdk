# !/usr/bin/env python3
# encoding: utf-8
from sys import exc_info
from traceback import extract_tb
from inspect import stack
from json import dumps
from json.decoder import JSONDecodeError
from typing import Union


def __getattr__(identifier: str) -> object:
    if stack()[1].filename.split('\\')[-1] not in ('qg_bot.py', 'qg_bot_ws.py', 'qg_bot_ws_async.py', 'model.py', 'api.py', 'async_api.py'):
        raise AssertionError("为SDK内部使用类，无法使用")

    return globals()[identifier.__path__]


def exception_handler(error):
    error_info = extract_tb(exc_info()[-1])[-1]
    return "[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0], error_info[1], error_info[2])


def objectize(data: dict, flag: bool = True):
    doc = dumps(data)
    if isinstance(data, dict):
        for keys, values in data.items():
            if keys.isnumeric():
                return data
            if isinstance(values, dict):
                data[keys] = objectize(values, False)
            elif isinstance(values, list):
                for i, items in enumerate(values):
                    if isinstance(items, dict):
                        data[keys][i] = objectize(items, False)
        object_data = type('object', (object,), data)
        if flag:
            setattr(object_data, '__doc__', doc)
        return object_data
    else:
        return None


def convert_color(color: Union[tuple, str]):
    colors = []
    if isinstance(color, tuple):
        if len(color) == 3:
            for items in color:
                if not isinstance(items, int) or items not in range(256):
                    raise TypeError('RGB颜色应为一个三位数的tuple，且当中每个数值都应该介乎于0和255之间，如(255,255,255)')
                colors.append(items)
        else:
            raise TypeError('RGB颜色应为一个三位数的tuple，且当中每个数值都应该介乎于0和255之间，如(255,255,255)')
    elif isinstance(color, str):
        colour = color.replace('#', '')
        if len(colour) == 6:
            for items in (colour[:2], colour[2:4], colour[4:]):
                try:
                    items = int(items, 16)
                except ValueError:
                    raise TypeError('该HEX颜色不存在，请检查其颜色值是否准确')
                if items not in range(256):
                    raise TypeError('该HEX颜色不存在，请检查其颜色值是否准确')
                colors.append(items)
        else:
            raise TypeError('HEX颜色应为一个 #加六位数字或字母 的string，如"#ffffff"')
    else:
        raise TypeError('颜色值应为RGB的三位数tuple，如(255,255,255)；或HEX的sting颜色，如"#ffffff"')
    return colors[0] + 256 * colors[1] + (256**2) * colors[2]


def treat_msg(raw_msg: str):
    if not raw_msg:
        return ''
    if raw_msg[0] == '/':
        raw_msg = raw_msg[1:]
    return raw_msg.strip().replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('\xa0', ' ')


def http_temp(return_, code: int):
    trace_id = return_.headers['X-Tps-Trace-Id']
    if return_.status_code == code:
        return objectize({'data': None, 'trace_id': trace_id, 'result': True})
    else:
        try:
            return_dict = return_.json()
            return objectize({'data': return_dict, 'trace_id': trace_id, 'result': False})
        except JSONDecodeError:
            return objectize({'data': None, 'trace_id': trace_id, 'result': False})


async def async_http_temp(return_, code: int):
    trace_id = return_.headers['X-Tps-Trace-Id']
    if return_.status == code:
        return objectize({'data': None, 'trace_id': trace_id, 'result': True})
    else:
        try:
            return_dict = await return_.json()
            return objectize({'data': return_dict, 'trace_id': trace_id, 'result': False})
        except JSONDecodeError:
            return objectize({'data': None, 'trace_id': trace_id, 'result': False})


def regular_temp(return_):
    trace_id = return_.headers['X-Tps-Trace-Id']
    try:
        return_dict = return_.json()
        if isinstance(return_dict, dict) and 'code' in return_dict.keys():
            result = False
        else:
            result = True
        return objectize({'data': return_dict, 'trace_id': trace_id, 'result': result})
    except JSONDecodeError:
        return objectize({'data': None, 'trace_id': trace_id, 'result': False})


async def async_regular_temp(return_):
    trace_id = return_.headers['X-Tps-Trace-Id']
    try:
        return_dict = await return_.json()
        if isinstance(return_dict, dict) and 'code' in return_dict.keys():
            result = False
        else:
            result = True
        return objectize({'data': return_dict, 'trace_id': trace_id, 'result': result})
    except JSONDecodeError:
        return objectize({'data': None, 'trace_id': trace_id, 'result': False})


def empty_temp(return_):
    trace_id = return_.headers['X-Tps-Trace-Id']
    try:
        return_dict = return_.json()
        if not return_dict:
            result = True
            return_dict = None
        else:
            result = False
        return objectize({'data': return_dict, 'trace_id': trace_id, 'result': result})
    except JSONDecodeError:
        return objectize({'data': None, 'trace_id': trace_id, 'result': False})


async def async_empty_temp(return_):
    trace_id = return_.headers['X-Tps-Trace-Id']
    try:
        return_dict = await return_.json()
        if not return_dict:
            result = True
            return_dict = None
        else:
            result = False
        return objectize({'data': return_dict, 'trace_id': trace_id, 'result': result})
    except JSONDecodeError:
        return objectize({'data': None, 'trace_id': trace_id, 'result': False})


def sdk_error_temp(message):
    return objectize({'data': {'code': -1, 'message': f'这是来自SDK的错误信息：{message}'}, 'trace_id': None,
                      'result': False})
