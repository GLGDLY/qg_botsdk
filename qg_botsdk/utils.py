#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具流
"""
from collections import namedtuple


def objectize(data):
    """
    将dict转为object
    :param data: dict格式的数据
    :return:
    """
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
        return namedtuple('object', data.keys())(*data.values())
    else:
        return None

