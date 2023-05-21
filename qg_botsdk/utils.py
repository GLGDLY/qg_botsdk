#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from io import IOBase
from typing import Any, Dict, Tuple, Union

try:
    from yaml import safe_load
except (ImportError, ModuleNotFoundError):
    safe_load = None


def read_yaml(target: Union[str, IOBase], encoding: str = "utf-8") -> Dict[str, Any]:
    if not safe_load:
        raise AssertionError("如需使用read_yaml函数，必须先pip install pyyaml")
    if isinstance(target, str):
        with open(target, "r", encoding=encoding) as f:
            return safe_load(f)
    elif isinstance(target, IOBase):
        return safe_load(target)
    else:
        raise TypeError("target应为str或IO")


def convert_color(color: Union[Tuple[int, int, int], str]):
    colors = []
    if isinstance(color, tuple):
        if len(color) == 3:
            for items in color:
                if not isinstance(items, int) or items not in range(256):
                    raise TypeError(
                        "RGB颜色应为一个三位数的tuple，且当中每个数值都应该介乎于0和255之间，如(255,255,255)"
                    )
                colors.append(items)
        else:
            raise TypeError("RGB颜色应为一个三位数的tuple，且当中每个数值都应该介乎于0和255之间，如(255,255,255)")
    elif isinstance(color, str):
        colour = color.replace("#", "")
        if len(colour) == 6:
            for items in (colour[:2], colour[2:4], colour[4:]):
                try:
                    items = int(items, 16)
                except ValueError:
                    raise TypeError("该HEX颜色不存在，请检查其颜色值是否准确") from None
                if items not in range(256):
                    raise TypeError("该HEX颜色不存在，请检查其颜色值是否准确")
                colors.append(items)
        else:
            raise TypeError('HEX颜色应为一个 #加六位数字或字母 的string，如"#ffffff"')
    else:
        raise TypeError('颜色值应为RGB的三位数tuple，如(255,255,255)；或HEX的sting颜色，如"#ffffff"')
    return colors[0] + 256 * colors[1] + (256**2) * colors[2]
