# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from asyncio import Lock as ALock
from asyncio import get_event_loop, new_event_loop, sleep
from importlib.machinery import SourceFileLoader
from os import getpid
from os.path import exists
from os.path import split as path_split
from re import Pattern
from threading import Lock as TLock
from time import sleep as t_sleep
from typing import Any, Callable, List, Optional, Union

from ._api_model import robot_model
from ._utils import check_func, exception_processor
from .api import API
from .async_api import AsyncAPI
from .http import Session
from .logger import Logger
from .model import Model
from .plugins import Plugins
from .qg_bot_ws import BotWs as _BotWs
from .version import __version__

pid = getpid()
print(f"本次程序进程ID：{pid} | SDK版本：{__version__} | 即将开始运行机器人……")
t_sleep(0.5)


class BOT:
    def __init__(
        self,
        bot_id: str,
        bot_token: str,
        bot_secret: Optional[str] = None,
        is_private: bool = False,
        is_sandbox: bool = False,
        no_permission_warning: bool = True,
        is_async: bool = False,
        is_retry: bool = True,
        is_log_error: bool = True,
        shard_no: int = 0,
        total_shard: int = 1,
        max_workers: int = 32,
        api_max_concurrency: int = 0,
    ):
        """
        机器人主体，输入BotAppID和密钥，并绑定函数后即可快速使用

        :param bot_id: 机器人平台后台BotAppID（开发者ID）项，必填
        :param bot_token: 机器人平台后台机器人令牌项，必填
        :param bot_secret: 机器人平台后台机器人密钥项（已废弃）
        :param is_private: 机器人是否为私域机器人，默认False
        :param is_sandbox: 是否开启沙箱环境，默认False
        :param no_permission_warning: 是否开启当机器人获取疑似权限不足的事件时的警告提示，默认开启
        :param is_async: 使用同步api还是异步api，默认False（使用同步）
        :param is_retry: 使用api时，如遇可重试的错误码是否自动进行重试，默认开启
        :param is_log_error: 使用api时，如返回的结果为不成功，可自动log输出报错信息，默认开启
        :param shard_no: 当前分片数，如不熟悉相关配置请不要轻易改动此项，默认0
        :param total_shard: 最大分片数，如不熟悉相关配置请不要轻易改动此项，默认1
        :param max_workers: 在同步模式下，允许同时运行的最大线程数，默认32
        :param api_max_concurrency: API允许的最大并发数，超过此并发数将进入队列，如此数值<=0代表不开启任何队列
        """
        self.logger = Logger(bot_id)
        self.bot_id = bot_id
        self.bot_token = bot_token
        if bot_secret:
            raise DeprecationWarning(
                "bot_secret已被废弃，如需使用安全接口，请通过security_setup()绑定小程序ID和secret"
            )
        self.is_private = is_private
        self.bot_url = (
            r"https://sandbox.api.sgroup.qq.com"
            if is_sandbox
            else r"https://api.sgroup.qq.com"
        )
        if not bot_id or not bot_token:
            raise type("IdTokenMissing", (Exception,), {})(
                "你还没有输入 bot_id 和 bot_token，无法连接使用机器人\n如尚未有相关票据，"
                "请参阅 https://qg-botsdk.readthedocs.io/zh_CN/latest/quick_start 了解相关详情"
            )
        try:
            self._loop = get_event_loop()
        except RuntimeError:
            self._loop = new_event_loop()
        self._intents = 0
        self._shard_no = shard_no
        self._total_shard = total_shard
        self._bot_class = None
        self._on_delete_function = None
        self._on_msg_function = None
        self._on_dm_function = None
        self._on_guild_event_function = None
        self._on_channel_event_function = None
        self._on_guild_member_function = None
        self._on_reaction_function = None
        self._on_interaction_function = None
        self._on_audit_function = None
        self._on_forum_function = None
        self._on_open_forum_function = None
        self._on_audio_function = None
        self._on_live_channel_member_function = None
        self._repeat_function = None
        self._on_start_function = None
        self.is_filter_self = True
        self.check_interval = 10
        self.__running = False
        self.__await_closure = False
        self.auth = f"Bot {bot_id}.{bot_token}"
        self.bot_headers = {"Authorization": self.auth}
        self._session = Session(
            self._loop,
            is_retry,
            is_log_error,
            self.logger,
            api_max_concurrency,
            headers=self.bot_headers,
        )
        self.msg_treat = True
        self.dm_treat = False
        self.no_permission_warning = no_permission_warning
        self.max_workers = max_workers
        self.is_async = is_async
        self.api: Union[AsyncAPI, API] = AsyncAPI(
            self.bot_url,
            self._session,
            self.logger,
            self._check_warning,
        )
        if not is_async:
            self.lock = TLock()
            self.api = API(self.api, self._loop)
        else:
            self.lock = ALock()

    def __repr__(self):
        return f"<qg_botsdk.BOT object [id: {self.bot_id}, token: {self.bot_token}]>"

    @property
    def robot(self) -> robot_model():
        return self._bot_class.robot

    @property
    def running(self):
        return self.__running

    @property
    def loop(self):
        return self._loop

    def load_default_msg_logger(self):
        """
        加载默认的消息日志模块，可以默认格式自动log记录接收到的用户消息
        """
        self.logger.info("加载默认消息日志模块成功")
        if "__sdk_default_logger" in Plugins.get_preprocessor_names():
            return

        def __sdk_default_logger(data: Model.MESSAGE):
            self.logger.info(
                f"收到频道 {data.guild_id} 用户 {data.author.username}({data.author.id}) "
                f"的消息：{data.treated_msg}"
            )

        Plugins.before_command()(__sdk_default_logger)

    @exception_processor
    def __time_event_run(self):
        if self.is_async:
            self._loop.create_task(self._repeat_function())
        else:
            self._repeat_function()

    async def __time_event_check(self):
        while self.__running:
            await sleep(self.check_interval)
            self.__time_event_run()

    def __register_msg_intents(self, is_log=True):
        if not self._intents >> 9 & 1 and not self._intents >> 30 & 1:
            if self.is_private:
                self._intents = self._intents | 1 << 9
                if is_log:
                    self.logger.info("消息（所有消息）接收函数订阅成功")
            else:
                self._intents = self._intents | 1 << 30
                if is_log:
                    self.logger.info("消息（艾特消息）接收函数订阅成功")

    def _get_plugins(self):
        commands, preprocessors = Plugins()
        if commands:
            for items in commands:
                check_func(items["func"], Model.MESSAGE, is_async=self.is_async)
            self.__register_msg_intents()
        for func in preprocessors:
            check_func(func, Model.MESSAGE, is_async=self.is_async)
        return commands, preprocessors

    @staticmethod
    def load_plugins(path_to_plugins: str):
        """
        用于加载插件的.py程序

        :param path_to_plugins: 指向相应.py插件文件的相对或绝对路径
        :return:
        """
        if not exists(path_to_plugins):
            raise ModuleNotFoundError(f"指向plugin的路径 [{path_to_plugins}] 并不存在")
        if not path_to_plugins.endswith(".py"):
            path_to_plugins += ".py"
        _name = path_split(path_to_plugins)[1][:-3]
        try:
            SourceFileLoader(_name, path_to_plugins).load_module()
            with open(path_to_plugins, "r", encoding="utf-8") as f:
                exec(f.read())
        except Exception:
            raise ImportError(f"plugin [{path_to_plugins}] 导入失败")

    @staticmethod
    def before_command():
        """
        注册预处理器，将在检查所有commands前执行
        """

        def wrap(func: Model.MESSAGE):
            Plugins.before_command()(func)
            return func

        return wrap

    @staticmethod
    def on_command(
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
        指令装饰器。用于快速注册消息事件，当连同bind_msg使用时，如没有触发短路，bind_msg注册的函数将在最后被调用

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
            Plugins.on_command(
                command,
                regex,
                is_treat,
                is_require_at,
                is_short_circuit,
                is_custom_short_circuit,
                is_require_admin,
                admin_error_msg,
            )(func)
            return func

        return wrap

    def bind_msg(
        self,
        on_msg_function: Callable[[Model.MESSAGE], Any] = None,
        treated_data: bool = True,
        all_msg: bool = None,
    ):
        """
        用作绑定接收消息的函数，将根据机器人是否公域自动判断接收艾特或所有消息

        :param on_msg_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        :param treated_data: 是否返回经转义处理的文本，如是则会在返回的Object中添加一个treated_msg的子类，默认True
        :param all_msg: 是否无视公私域限制，强制开启全部消息接收，默认None（不判断此项参数）
        """

        def wraps(func):
            check_func(func, Model.MESSAGE, is_async=self.is_async)
            self._on_msg_function = func
            if not treated_data:
                self.msg_treat = False
            if all_msg is None:
                self.__register_msg_intents()
            elif all_msg:
                self._intents = self._intents | 1 << 9
                self.logger.info("消息（所有消息）接收函数订阅成功")
            else:
                self._intents = self._intents | 1 << 30
                self.logger.info("消息（艾特消息）接收函数订阅成功")

        if not on_msg_function:
            return wraps
        wraps(on_msg_function)

    def bind_dm(
        self,
        on_dm_function: Callable[[Model.DIRECT_MESSAGE], Any] = None,
        treated_data: bool = True,
    ):
        """
        用作绑定接收私信消息的函数

        :param on_dm_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        :param treated_data: 是否返回经转义处理的文本，如是则会在返回的Object中添加一个treated_msg的子类，默认True
        """

        def wraps(func):
            check_func(func, Model.DIRECT_MESSAGE, is_async=self.is_async)
            self._on_dm_function = func
            self._intents = self._intents | 1 << 12
            if treated_data:
                self.dm_treat = True
            self.logger.info("私信接收函数订阅成功")

        if not on_dm_function:
            return wraps
        wraps(on_dm_function)

    def bind_msg_delete(
        self,
        on_delete_function: Callable[[Model.MESSAGE_DELETE], Any] = None,
        is_filter_self: bool = True,
    ):
        """
        用作绑定接收消息撤回事件的函数，注册时将自动根据公域私域注册艾特或全部消息，但不会主动注册私信事件

        :param on_delete_function:类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        :param is_filter_self: 是否过滤用户自行撤回的消息，只接受管理撤回事件
        """

        def wraps(func):
            check_func(func, Model.MESSAGE_DELETE, is_async=self.is_async)
            self._on_delete_function = func
            self.is_filter_self = is_filter_self
            self.__register_msg_intents(False)
            self.logger.info("撤回事件订阅成功")

        if not on_delete_function:
            return wraps
        wraps(on_delete_function)

    def bind_guild_event(
        self, on_guild_event_function: Callable[[Model.GUILDS], Any] = None
    ):
        """
        用作绑定接收频道信息的函数

        :param on_guild_event_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            check_func(func, Model.GUILDS, is_async=self.is_async)
            self._on_guild_event_function = func
            self._intents = self._intents | 1
            self.logger.info("频道事件订阅成功")

        if not on_guild_event_function:
            return wraps
        wraps(on_guild_event_function)

    def bind_channel_event(
        self, on_channel_event_function: Callable[[Model.CHANNELS], Any] = None
    ):
        """
        用作绑定接收子频道信息的函数

        :param on_channel_event_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            check_func(func, Model.CHANNELS, is_async=self.is_async)
            self._on_channel_event_function = func
            self._intents = self._intents | 1
            self.logger.info("子频道事件订阅成功")

        if not on_channel_event_function:
            return wraps
        wraps(on_channel_event_function)

    def bind_guild_member(
        self, on_guild_member_function: Callable[[Model.GUILD_MEMBERS], Any] = None
    ):
        """
        用作绑定接收频道成员信息的函数

        :param on_guild_member_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            check_func(func, Model.GUILD_MEMBERS, is_async=self.is_async)
            self._on_guild_member_function = func
            self._intents = self._intents | 1 << 1
            self.logger.info("频道成员事件订阅成功")

        if not on_guild_member_function:
            return wraps
        wraps(on_guild_member_function)

    def bind_reaction(
        self, on_reaction_function: Callable[[Model.REACTION], Any] = None
    ):
        """
        用作绑定接收表情表态信息的函数

        :param on_reaction_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            check_func(func, Model.REACTION, is_async=self.is_async)
            self._on_reaction_function = func
            self._intents = self._intents | 1 << 10
            self.logger.info("表情表态事件订阅成功")

        if not on_reaction_function:
            return wraps
        wraps(on_reaction_function)

    def bind_interaction(
        self, on_interaction_function: Callable[[Model.INTERACTION], Any] = None
    ):
        """
        用作绑定接收互动事件的函数

        :param on_interaction_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            check_func(func, Model.INTERACTION, is_async=self.is_async)
            self._on_interaction_function = func
            self._intents = self._intents | 1 << 26
            self.logger.info("互动事件订阅成功")

        if not on_interaction_function:
            return wraps
        wraps(on_interaction_function)

    def bind_audit(
        self, on_audit_function: Callable[[Model.MESSAGE_AUDIT], Any] = None
    ):
        """
        用作绑定接收审核事件的函数

        :param on_audit_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            check_func(func, Model.MESSAGE_AUDIT, is_async=self.is_async)
            self._on_audit_function = func
            self._intents = self._intents | 1 << 27
            self.logger.info("审核事件订阅成功")

        if not on_audit_function:
            return wraps
        wraps(on_audit_function)

    def bind_forum(self, on_forum_function: Callable[[Model.FORUMS_EVENT], Any] = None):
        """
        用作绑定接收论坛事件的函数，一般仅私域机器人能注册此事件

        .. note::
            当前仅可以接收FORUM_THREAD_CREATE、FORUM_THREAD_UPDATE、FORUM_THREAD_DELETE三个事件

        :param on_forum_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            check_func(func, Model.FORUMS_EVENT, is_async=self.is_async)
            self._on_forum_function = func
            self._intents = self._intents | 1 << 28
            self.logger.info("论坛事件订阅成功")
            if not self.is_private and self.no_permission_warning:
                self.logger.warning("请注意，一般公域机器人并不能注册论坛事件，请检查自身是否拥有相关权限")

        if not on_forum_function:
            return wraps
        wraps(on_forum_function)

    def bind_open_forum(
        self, on_open_forum_function: Callable[[Model.OPEN_FORUMS], Any] = None
    ):
        """
        用作绑定接收公域论坛事件的函数

        .. note::
            当前仅可以接收FORUM_THREAD_CREATE、FORUM_THREAD_UPDATE、FORUM_THREAD_DELETE三个事件

        :param on_open_forum_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            check_func(func, Model.OPEN_FORUMS, is_async=self.is_async)
            self._on_open_forum_function = func
            self._intents = self._intents | 1 << 18
            self.logger.info("论坛事件订阅成功")

        if not on_open_forum_function:
            return wraps
        wraps(on_open_forum_function)

    def bind_audio(self, on_audio_function: Callable[[Model.AUDIO_ACTION], Any] = None):
        """
        用作绑定接收论坛事件的函数

        :param on_audio_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            check_func(func, Model.AUDIO_ACTION, is_async=self.is_async)
            self._on_audio_function = func
            self._intents = self._intents | 1 << 29
            self.logger.info("音频事件订阅成功")
            if self.no_permission_warning:
                self.logger.warning("请注意，一般机器人并不能注册音频事件（需先进行申请），请检查自身是否拥有相关权限")

        if not on_audio_function:
            return wraps
        wraps(on_audio_function)

    def bind_live_channel_member(
        self,
        on_live_channel_member_function: Callable[
            [Model.LIVE_CHANNEL_MEMBER], Any
        ] = None,
    ):
        """
        用作绑定接收音视频/直播子频道成员进出事件的函数

        :param on_live_channel_member_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            check_func(func, Model.LIVE_CHANNEL_MEMBER, is_async=self.is_async)
            self._on_live_channel_member_function = func
            self._intents = self._intents | 1 << 19
            self.logger.info("音视频/直播子频道成员进出事件订阅成功")

        if not on_live_channel_member_function:
            return wraps
        wraps(on_live_channel_member_function)

    def register_repeat_event(
        self,
        time_function: Callable[[], Any] = None,
        check_interval: Union[float, int] = 10,
    ):
        """
        用作注册重复事件的函数，注册并开始机器人后，会根据间隔时间不断调用注册的函数

        :param time_function: 类型为function，该函数不应包含任何参数
        :param check_interval: 每多少秒检查调用一次时间事件函数，默认10
        """

        def wraps(func):
            check_func(func, is_async=self.is_async)
            self._repeat_function = func
            self.check_interval = check_interval
            self.logger.info("重复运行事件注册成功")

        if not time_function:
            return wraps
        wraps(time_function)

    def register_start_event(self, on_start_function: Callable[[], Any] = None):
        """
        用作注册机器人开始时运行的函数，此函数不应有无限重复的内容

        :param on_start_function: 类型为function，该函数不应包含任何参数
        """

        def wraps(func):
            check_func(func, is_async=self.is_async)
            self._on_start_function = func
            self.logger.info("初始事件注册成功")

        if not on_start_function:
            return wraps
        wraps(on_start_function)

    def security_setup(self, mini_id: str, mini_secret: str):
        """
        用于注册小程序ID和secret以使用腾讯内容安全接口

        :param mini_id: 小程序ID
        :param mini_secret: 小程序secret
        """
        self.api.security_setup(mini_id, mini_secret)

    def _check_warning(self, name: str):
        if not self.is_private and self.no_permission_warning:
            self.logger.warning(f"请注意，一般公域机器人并不能使用{name}API，请检查自身是否拥有相关权限")

    def start(self, is_blocking: bool = True):
        """
        开始运行机器人的函数，在唤起此函数后的代码将不能运行，如需非阻塞性运行，请传入is_blocking=False，以下是一个简单的唤起流程：

        >>> from qg_botsdk import BOT
        >>> bot = BOT(bot_id='xxx', bot_token='xxx')
        >>> bot.start()

        .. seealso::
            更多教程和相关资讯可参阅：
            https://qg-botsdk.readthedocs.io/zh_CN/latest/index.html

        :param is_blocking: 机器人是否阻塞运行，如选择False，机器人将以异步任务的方式非阻塞性运行，如不熟悉异步编程请不要使用此项
        """
        try:
            if not self.__running and not self._bot_class:
                self.__running = True
                gateway = self._loop.run_until_complete(
                    self._session.get(f"{self.bot_url}/gateway/bot")
                )
                gateway = self._loop.run_until_complete(gateway.json())
                url = gateway.get("url")
                if not url:
                    raise type("IdTokenError", (Exception,), {})(
                        "你输入的 bot_id 和/或 bot_token 错误，无法连接使用机器人\n如尚未有相关票据，"
                        "请参阅 https://qg-botsdk.readthedocs.io/zh_CN/latest/quick_start 了解相关详情"
                    )
                self.logger.debug("[机器人ws地址] " + url)
                commands, preprocessors = self._get_plugins()
                if self._repeat_function is not None:
                    self._loop.create_task(self.__time_event_check())
                self._bot_class = _BotWs(
                    self._session,
                    self.logger,
                    self._total_shard,
                    self._shard_no,
                    url,
                    self.auth,
                    self._on_msg_function,
                    self._on_dm_function,
                    self._on_delete_function,
                    self.is_filter_self,
                    self._on_guild_event_function,
                    self._on_channel_event_function,
                    self._on_guild_member_function,
                    self._on_reaction_function,
                    self._on_interaction_function,
                    self._on_audit_function,
                    self._on_forum_function,
                    self._on_open_forum_function,
                    self._on_audio_function,
                    self._on_live_channel_member_function,
                    self._intents,
                    self.msg_treat,
                    self.dm_treat,
                    self._on_start_function,
                    self.is_async,
                    self.max_workers,
                    self.api,
                    commands,
                    preprocessors,
                )
                if is_blocking:
                    self._loop.run_until_complete(self._bot_class.starter())
                else:
                    self._loop.create_task(self._bot_class.starter())
            else:
                self.logger.error("当前机器人已在运行中！")
        except KeyboardInterrupt:
            self.logger.info("结束运行机器人（KeyboardInterrupt）")
            exit()

    def block(self):
        """
        当BOT.start()选择is_blocking=False的非阻塞性运行时，此函数能在后续阻塞主进程而继续运行机器人
        """
        try:
            while self.__running or self.__await_closure:
                self._loop.run_until_complete(sleep(1))
        except KeyboardInterrupt:
            self.logger.info("结束运行机器人（KeyboardInterrupt）")
            exit()

    def close(self):
        """
        结束运行机器人的函数

        .. seealso::
            更多教程和相关资讯可参阅：
            https://qg-botsdk.readthedocs.io/zh_CN/latest/index.html
        """
        if self.__running:
            self.__await_closure = True
            self.__running = False
            self.logger.info("WS链接已开始结束进程，请等待另一端完成握手并等待 TCP 连接终止")
            self._bot_class.running = False
            timeout = self._loop.time() + 60
            while self._loop.time() < timeout:
                t_sleep(1)
                if not self._bot_class or self._bot_class.ws.closed:
                    self.__await_closure = False
                    return
            self._bot_class = None
            self.logger.info("判断超时，WS链接已强制结束")
            self.__await_closure = False
        else:
            self.logger.error("当前机器人没有运行！")
