# !/usr/bin/env python3
# encoding: utf-8
from inspect import stack
from json import dumps


def __getattr__(identifier: str) -> object:
    if stack()[1].filename.split('\\')[-1] not in ('qg_bot.py', 'qg_bot_ws.py', 'qg_bot_ws_async.py', 'model.py'):
        raise AssertionError("为SDK内部使用类，无法使用")

    return globals()[identifier.__path__]


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


def convert_color(color: tuple or str):
    colors = []
    if isinstance(color, tuple):
        if len(color) == 3:
            for items in color:
                if not isinstance(items, int) or items > 255 or items < 0:
                    raise TypeError('RGB颜色应为一个三位数的tuple，且当中每个数值都应该介乎于0和255之间，如(255,255,255)')
                colors.append(int(items))
        else:
            raise TypeError('RGB颜色应为一个三位数的tuple，且当中每个数值都应该介乎于0和255之间，如(255,255,255)')
    elif isinstance(color, str):
        colour = color.replace('#', '')
        if len(colour) == 6:
            for items in [colour[:2], colour[2:4], colour[4:]]:
                try:
                    local_colour = int(items, 16)
                except ValueError:
                    raise TypeError('该HEX颜色不存在，请检查其颜色值是否准确')
                if local_colour > 255 or local_colour < 0:
                    raise TypeError('该HEX颜色不存在，请检查其颜色值是否准确')
                colors.append(local_colour)
        else:
            raise TypeError('HEX颜色应为一个 #加六位数字或字母 的string，如"#ffffff"')
    else:
        raise TypeError('颜色值应为RGB的三位tuple，如(255,255,255)；或HEX的sting颜色，如"#ffffff"')
    return colors[0] + 256 * colors[1] + 256 * 256 * colors[2]
