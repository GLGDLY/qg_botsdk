#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from re import compile as re_compile
from typing import List, Optional, Pattern, Union

from .model import Model


class Plugins:
    _commands = []
    _preprocessors = []

    def __new__(cls) -> tuple:
        commands, preprocessors = cls._commands, cls._preprocessors
        cls._commands, cls._preprocessors = [], []
        return commands, preprocessors

    @classmethod
    def get_preprocessor_names(cls):
        return (func.__name__ for func in cls._preprocessors)

    @classmethod
    def get_commands_names(cls):
        return (func.__name__ for func in cls._commands)

    @classmethod
    def before_command(cls):
        """
        注册plugins预处理器，将在检查所有commands前执行
        """

        def wrap(func: Model.MESSAGE):
            cls._preprocessors.append(func)
            return func

        return wrap

    @classmethod
    def on_command(
        cls,
        command: Optional[Union[List[str], str]] = None,
        regex: Optional[Union[Pattern, str]] = None,
        is_treat: bool = True,
        is_require_at: bool = False,
        is_short_circuit: bool = True,
        is_custom_short_circuit: bool = False,
        is_require_admin: bool = False,
        admin_error_msg: Optional[str] = None,
    ):
        """
        注册plugins指令装饰器，可用于分割式编写指令并注册进机器人

        :param command: 可触发事件的指令列表，与正则regex互斥，优先使用此项
        :param regex: 可触发指令的正则compile实例或正则表达式，与指令表互斥
        :param is_treat: 是否在treated_msg中同时处理指令，如正则将返回.groups()，默认是
        :param is_require_at: 是否要求必须艾特机器人才能触发指令，默认否
        :param is_short_circuit: 如果触发指令成功是否短路不运行后续指令（将根据注册顺序排序指令的短路机制），默认是
        :param is_custom_short_circuit: 如果触发指令成功而返回True则不运行后续指令，与is_short_circuit不能同时存在，默认否
        :param is_require_admin: 是否要求频道主或或管理才可触发指令，默认否
        :param admin_error_msg: 当is_require_admin为True，而触发用户的权限不足时，如此项不为None，返回此消息并短路；否则不进行短路
        """

        def wrap(func: Model.MESSAGE):
            if is_short_circuit and is_custom_short_circuit:
                raise AttributeError(
                    "注意is_short_circuit与is_custom_short_circuit存在冲突，不可同时为True"
                )
            if command:
                if isinstance(command, str):
                    cls._commands.append(
                        {
                            "command": [command],
                            "func": func,
                            "treat": is_treat,
                            "at": is_require_at,
                            "short_circuit": is_short_circuit,
                            "is_custom_short_circuit": is_custom_short_circuit,
                            "admin": is_require_admin,
                            "admin_error_msg": admin_error_msg,
                        }
                    )
                elif isinstance(command, list):
                    cls._commands.append(
                        {
                            "command": command,
                            "func": func,
                            "treat": is_treat,
                            "at": is_require_at,
                            "short_circuit": is_short_circuit,
                            "is_custom_short_circuit": is_custom_short_circuit,
                            "admin": is_require_admin,
                            "admin_error_msg": admin_error_msg,
                        }
                    )
                else:
                    raise TypeError("command参数仅接受str或list类型的指令内容")
            else:
                if isinstance(regex, str):
                    cls._commands.append(
                        {
                            "regex": re_compile(regex),
                            "func": func,
                            "treat": is_treat,
                            "at": is_require_at,
                            "short_circuit": is_short_circuit,
                            "is_custom_short_circuit": is_custom_short_circuit,
                            "admin": is_require_admin,
                            "admin_error_msg": admin_error_msg,
                        }
                    )
                elif isinstance(regex, Pattern):
                    cls._commands.append(
                        {
                            "regex": regex,
                            "func": func,
                            "treat": is_treat,
                            "at": is_require_at,
                            "short_circuit": is_short_circuit,
                            "is_custom_short_circuit": is_custom_short_circuit,
                            "admin": is_require_admin,
                            "admin_error_msg": admin_error_msg,
                        }
                    )
                else:
                    raise TypeError("regex参数仅接受re.compile返回的实例或str类型的正则表达式")
            return func

        return wrap
