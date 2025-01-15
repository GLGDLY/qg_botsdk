#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from re import compile as re_compile
from typing import Any, Callable, Dict, Iterable, List, Optional, Pattern, Tuple, Union

from ._statics import TraceNames
from ._utils import TraceCallerData
from .api import API
from .async_api import AsyncAPI
from .logger import Logger
from .model import BotCommandObject, CommandValidScenes, Model
from .session import AbstractSessionManager, SessionPatcher


class Plugins:
    _commands: List[BotCommandObject] = []
    _preprocessors: Dict[
        int,
        List[
            Callable[
                [Union[Model.MESSAGE, Model.GROUP_MESSAGE, Model.C2C_MESSAGE]], Any
            ]
        ],
    ] = {1 << x: [] for x in range(CommandValidScenes.ALL.bit_length())}
    api: Union[API, AsyncAPI] = TraceCallerData(TraceNames, ("self", "api"))
    logger: Logger = TraceCallerData(TraceNames, ("self", "logger"))
    session: AbstractSessionManager = SessionPatcher()

    def __new__(
        cls,
        bot_id=None,
        api=None,
        logger=None,
    ) -> Tuple[List, Dict[int, List]]:
        commands, preprocessors = cls._commands, cls._preprocessors
        cls._commands, cls._preprocessors = [], {
            1 << x: [] for x in range(CommandValidScenes.ALL.bit_length())
        }
        return commands, preprocessors

    @classmethod
    def get_preprocessor_names(cls):
        return (
            func.__name__ for funcs in cls._preprocessors.values() for func in funcs
        )

    @classmethod
    def get_commands_names(cls):
        return (x.func.__name__ for x in cls._commands)

    @classmethod
    def before_command(
        cls,
        valid_scenes: CommandValidScenes = CommandValidScenes.GUILD
        | CommandValidScenes.DM,
    ):
        """
        注册plugins预处理器，将在检查所有commands前执行

        :param valid_scenes: 此处理器的有效场景，可传入多个场景，默认 CommandValidScenes.GUILD|CommandValidScenes.DM
        """

        def wrap(
            func: Callable[
                [
                    Union[
                        Model.MESSAGE,
                        Model.DIRECT_MESSAGE,
                        Model.GROUP_MESSAGE,
                        Model.C2C_MESSAGE,
                    ]
                ],
                Any,
            ]
        ):
            # cls._preprocessors.append(func)
            for bit in range(CommandValidScenes.ALL.bit_length()):
                current_bit = 1 << bit
                if current_bit & valid_scenes:
                    cls._preprocessors[current_bit].append(func)
            return func

        return wrap

    @classmethod
    def on_command(
        cls,
        command: Optional[Union[Iterable[str], str]] = None,
        regex: Optional[Union[Pattern, str, Iterable[Union[Pattern, str]]]] = None,
        is_treat: bool = True,
        is_require_at: bool = False,
        is_short_circuit: bool = True,
        is_custom_short_circuit: bool = False,
        is_require_admin: bool = False,
        admin_error_msg: Optional[str] = None,
        valid_scenes: CommandValidScenes = CommandValidScenes.GUILD
        | CommandValidScenes.DM,
    ):
        """
        注册plugins指令装饰器，可用于分割式编写指令并注册进机器人

        :param command: 可触发事件的指令列表，与正则regex互斥，优先使用此项
        :param regex: 可触发指令的正则compile实例或正则表达式，与指令表互斥
        :param is_treat: 是否在treated_msg中同时处理指令，如正则将返回.groups()，默认是
        :param is_require_at: 是否要求必须艾特机器人才能触发指令，默认否
        :param is_short_circuit: 如果触发指令成功是否短路不运行后续指令（将根据注册顺序排序指令的短路机制），默认是
        :param is_custom_short_circuit: 如果触发指令成功而回调函数返回True则不运行后续指令，存在时优先于is_short_circuit，默认否
        :param is_require_admin: 是否要求频道主或或管理才可触发指令，默认否
        :param admin_error_msg: 当is_require_admin为True，而触发用户的权限不足时，如此项不为None，返回此消息并短路；否则不进行短路
        :param valid_scenes: 此机器人命令的有效场景，可传入多个场景，默认 CommandValidScenes.GUILD|CommandValidScenes.DM
        """

        def wrap(
            func: Callable[
                [Union[Model.MESSAGE, Model.GROUP_MESSAGE, Model.C2C_MESSAGE]], Any
            ]
        ):
            if is_short_circuit and is_custom_short_circuit:
                print(
                    "注意is_short_circuit与is_custom_short_circuit同时存在，将优先使用is_custom_short_circuit"
                )
            _kwargs = {
                "func": func,
                "treat": is_treat,
                "at": is_require_at,
                "short_circuit": is_short_circuit,
                "is_custom_short_circuit": is_custom_short_circuit,
                "admin": is_require_admin,
                "admin_error_msg": admin_error_msg,
                "valid_scenes": valid_scenes,
            }
            if command:
                if isinstance(command, str):
                    command_obj = BotCommandObject(command=[command], **_kwargs)
                elif isinstance(command, Iterable):
                    command_obj = BotCommandObject(command=command, **_kwargs)
                else:
                    raise TypeError("command参数仅接受str或list类型的指令内容")
            else:
                if isinstance(regex, str):
                    command_obj = BotCommandObject(regex=[re_compile(regex)], **_kwargs)
                elif isinstance(regex, Pattern):
                    command_obj = BotCommandObject(regex=[regex], **_kwargs)
                elif isinstance(regex, Iterable):
                    regexs = []
                    for x in regex:
                        if isinstance(x, str):
                            regexs.append(re_compile(x))
                        elif isinstance(x, Pattern):
                            regexs.append(x)
                        else:
                            raise TypeError(
                                "regex参数仅接受re.compile返回的实例或str类型的正则表达式"
                            )
                    command_obj = BotCommandObject(regex=regexs, **_kwargs)
                else:
                    raise TypeError(
                        "regex参数仅接受re.compile返回的实例或str类型的正则表达式"
                    )
            cls._commands.append(command_obj)
            return func

        return wrap
