from typing import Optional, Union, List, Pattern
from re import compile as re_compile

from .model import Model
from ._utils import check_func


class Plugins:
    _commands = {}
    _regex_commands = {}

    def __new__(cls, bot):
        for k, v in cls._commands.items():
            check_func(v['func'], Model.MESSAGE, is_async=bot.is_async)
        for k, v in cls._regex_commands.items():
            check_func(v['func'], Model.MESSAGE, is_async=bot.is_async)
        return cls._commands, cls._regex_commands

    @classmethod
    def on_command(cls, command: Optional[Union[List[str], str]] = None, regex: Optional[Union[Pattern, str]] = None,
                   is_treat: bool = True, is_require_at: bool = False, is_short_circuit: bool = False,
                   is_require_admin: bool = False,
                   ):
        """
        指令装饰器。用于快速注册消息事件

        :param command: 可触发事件的指令列表，与正则regex互斥，优先使用此项
        :param regex: 可触发指令的正则compile实例或正则表达式，与指令表互斥
        :param is_treat: 是否在treated_msg中同时处理指令，如正则将返回.groups()，默认是
        :param is_require_at: 是否要求必须艾特机器人才能触发指令，默认否
        :param is_short_circuit: 如果触发指令成功是否短路不运行后续指令（将根据注册顺序和command先regex后排序指令的短路机制），默认否
        :param is_require_admin: 是否要求频道主或或管理才可触发指令，默认否
        """

        def wrap(func):
            if command:
                if isinstance(command, str):
                    cls._commands[command] = {'func': func, 'treat': is_treat, 'at': is_require_at,
                                              'short_circuit': is_short_circuit, 'admin': is_require_admin}
                else:
                    for com in command:
                        cls._commands[com] = {'func': func, 'treat': is_treat, 'at': is_require_at,
                                              'short_circuit': is_short_circuit, 'admin': is_require_admin}
            else:
                if isinstance(regex, str):
                    cls._regex_commands[re_compile(regex)] = {'func': func, 'treat': is_treat, 'at': is_require_at,
                                                              'short_circuit': is_short_circuit,
                                                              'admin': is_require_admin}
                elif isinstance(regex, Pattern):
                    cls._regex_commands[regex] = {'func': func, 'treat': is_treat, 'at': is_require_at,
                                                  'short_circuit': is_short_circuit, 'admin': is_require_admin}
                else:
                    raise TypeError('regex参数仅接受re.compile返回的实例或str类型的正则表达式')
            return func

        return wrap
