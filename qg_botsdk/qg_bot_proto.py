#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from asyncio import AbstractEventLoop, sleep
from concurrent.futures import ThreadPoolExecutor
from copy import copy, deepcopy
from ssl import create_default_context
from typing import Any, Callable, Dict, List, Union

from ._api_model import StrPtr
from ._event import object_class
from ._proto_events_conversion import EVENTS_TO_DISPATCH, EVENTS_TO_MODEL
from ._seq_cache import SeqCache
from ._session import SessionManager
from ._statics import EVENTS, EVENTS_ENUM
from ._utils import exception_processor, objectize, treat_msg, treat_thread
from .api import API
from .async_api import AsyncAPI
from .logger import Logger
from .model import BotCommandObject, CommandValidScenes, Model
from .proto import proto
from .sandbox import SandBox


class BotProto:
    def __init__(
        self,
        bot_id: str,
        bot_token: str,
        bot_secret: str,
        loop: AbstractEventLoop,
        logger: Logger,
        access_token: StrPtr,
        func_registers: Dict,
        intents: int,
        msg_treat: bool,
        dm_treat: bool,
        on_start_function: Callable[[], Any],
        check_interval: int,
        repeat_function: Callable[[], Any],
        is_async: bool,
        max_workers: int,
        api: Union[AsyncAPI, API],
        commands: List[BotCommandObject],
        preprocessors: Dict[
            CommandValidScenes,
            List[
                Callable[
                    [Union[Model.MESSAGE, Model.GROUP_MESSAGE, Model.C2C_MESSAGE]], Any
                ]
            ],
        ],
        session_manager: SessionManager,
        protocol: proto.Proto,
        sandbox: SandBox,
    ):
        """
        此为SDK内部使用类，注册机器人请使用from qg_botsdk.qg_bot import BOT

        .. seealso::
            更多教程和相关资讯可参阅：
            https://qg-botsdk.readthedocs.io/zh_CN/latest/快速入门.html
        """
        self._bot_id = bot_id
        self._bot_token = bot_token
        self._bot_secret = bot_secret
        self._ssl = create_default_context()
        self.logger = logger
        self.auth = access_token if bot_secret else f"Bot {bot_id}.{bot_token}"
        self.on_start_function = on_start_function
        self.check_interval = check_interval
        self.repeat_function = repeat_function
        self.func_registers = func_registers
        if not intents and isinstance(protocol, proto.WS):
            self.logger.warning(
                "当前未订阅任何事件，将无法接收任何消息，只能使用主动消息功能"
            )
            intents = 1
        self.intents = intents
        self.msg_treat = msg_treat
        self.dm_treat = dm_treat
        self.robot = None
        self.loop = loop
        self.s = None
        self.reconnect_times = 0
        self.is_reconnect = False
        self.running = True
        self.session_id = 0
        self.is_first_run = False
        self.heartbeat = None
        self.is_async = is_async
        self.threads = ThreadPoolExecutor(max_workers) if not self.is_async else None
        self.api = api
        self.raw_api: AsyncAPI = api if is_async else api._api
        self.commands = commands
        self.preprocessors = preprocessors
        self.session_manager = session_manager
        self.at = "<@!%s>"
        self.skip_connect_waiting = False

        self.protocol = protocol(
            raw_api=self.raw_api,
            intents=intents,
            auth=self.auth,
            logger=logger,
            loop=loop,
            dispatch_func=self.dispatch_events,
        )
        self.sandbox = sandbox
        self.seq_cache = SeqCache()

    @exception_processor
    async def _time_event_run(self):
        if self.is_async:
            self.loop.create_task(self.repeat_function())
        else:
            self.threads.submit(self.repeat_function)

    async def _time_event_check(self):
        while self.running:
            await sleep(self.check_interval)
            await self._time_event_run()

    async def _start_event(self):
        self.is_first_run = True
        self.robot = await self.get_robot_info()
        self.at = self.at % self.robot.id
        self.logger.info(f"当前机器人ID：{self.robot.id}")
        if self.on_start_function is not None:
            if self.is_async:
                self.loop.create_task(
                    self.async_start_callback_task(self.on_start_function)
                )
            else:
                self.threads.submit(self.start_callback_task, self.on_start_function)
        if self.repeat_function is not None:
            self.loop.create_task(self._time_event_check())

    async def get_robot_info(self, retry=False):
        robot_info = await self.raw_api.get_bot_info()
        if not robot_info.result or robot_info.data.id is None:
            if not retry:
                return self.get_robot_info(retry)
            else:
                self.logger.error(
                    "获取当前机器人信息失败，机器人启动失败，程序将退出运行（可重试）"
                )
                exit()
        return robot_info.data

    @exception_processor
    async def async_start_callback_task(self, func, *args):
        return await func(*args)

    @exception_processor
    def start_callback_task(self, func, *args):
        return func(*args)

    @exception_processor
    async def distribute(
        self,
        function,
        data: Dict = None,
        objectized_data: object_class = None,
    ):
        if function:
            if not objectized_data:
                objectized_data = objectize(data.get("d", {}), self.api, self.is_async)
            t = getattr(objectized_data, "t", None)
            model_class = EVENTS_TO_MODEL.get(t, None)
            if model_class and model_class not in objectized_data.__class__.__bases__:
                objectized_data.__class__.__bases__ += (model_class,)
            if not self.is_async:
                return self.threads.submit(
                    self.start_callback_task, function, objectized_data
                )
            else:
                return self.loop.create_task(
                    self.async_start_callback_task(function, objectized_data)
                )

    @exception_processor
    def treat_command(
        self, objectized_data: Model.MESSAGE, treated_msg, command=None, regex=None
    ):
        if self.msg_treat:
            msg = treated_msg
            # deepcopy treated_msg with just shallow copy others
            # resulting that changing of treated msg will not affect other commands
            memo = {}
            for x in objectized_data.__dict__:
                if x != "treated_msg":
                    memo[id(getattr(objectized_data, x))] = copy(
                        getattr(objectized_data, x)
                    )
            objectized_data = deepcopy(objectized_data, memo)
            objectized_data.treated_msg = (
                msg[msg.find(command) + len(command) :].strip()
                if command is not None
                else regex.groups()
            )
        return objectized_data

    @exception_processor
    async def check_command(
        self,
        objectized_data: Model.MESSAGE,
        treated_msg: str,
        command_obj: BotCommandObject,
        **kwargs,
    ):
        if command_obj.admin:
            try:
                roles = objectized_data.member.roles
            except Exception:
                command_str = kwargs.get("command") or getattr(
                    kwargs.get("regex"), "pattern", None
                )
                self.logger.error(
                    f"cannot check roles of member for admin command: {command_str}"
                )
                return False
            if "2" not in roles and "4" not in roles:  # if not admin
                if command_obj.admin_error_msg:
                    if self.is_async:
                        self.loop.create_task(
                            objectized_data.reply(
                                command_obj.admin_error_msg,
                            )
                        )
                    else:
                        self.threads.submit(
                            objectized_data.reply,
                            command_obj.admin_error_msg,
                        )
                    return True
                return False
        if command_obj.treat:
            objectized_data = self.treat_command(objectized_data, treated_msg, **kwargs)
        task = await self.distribute(command_obj.func, objectized_data=objectized_data)
        if not command_obj.is_custom_short_circuit:
            return command_obj.short_circuit  # True or False
        else:
            while not task.done():
                await sleep(0.1)
            r = task.result()
            return r  # True or False

    def process_wait_for_commands(
        self, current_scene: CommandValidScenes, objectized_data, msg, treated_msg
    ):
        try:
            wait_for_commands = self.session_manager.wait_for_message_checker(
                objectized_data
            )
            for x in wait_for_commands:
                if x.command.valid_scenes & current_scene == 0:
                    continue
                commands = x.command.command
                regexs = x.command.regex
                if commands:
                    for command in commands:
                        if command in msg and (not x.command.at or self.at in msg):
                            if x.command.treat:
                                objectized_data = self.treat_command(
                                    objectized_data, treated_msg, command=command
                                )
                            x.callback(objectized_data)
                            if x.command.short_circuit:
                                return True
                            break
                else:
                    for regex in regexs:
                        regex = regex.search(msg)
                        if regex and (not x.command.at or self.at in msg):
                            if x.command.treat:
                                objectized_data = self.treat_command(
                                    objectized_data, treated_msg, regex=regex
                                )
                            x.callback(objectized_data)
                            if x.command.short_circuit:
                                return True
                            break
        except Exception:
            pass
        return False

    @exception_processor
    async def distribute_commands(
        self, current_scene: CommandValidScenes, data: Dict, treated_msg: str
    ):
        objectized_data = objectize(data.get("d", {}), self.api, self.is_async)
        # run preprocessors
        for scene, funcs in self.preprocessors.items():
            if scene & current_scene == 0:
                continue
            for func in funcs:
                await self.distribute(func, objectized_data=objectized_data)
        # check commands
        msg = data.get("d", {}).get("content", "")
        if self.process_wait_for_commands(
            current_scene, objectized_data, msg, treated_msg
        ):
            return True

        for items in self.commands:
            if items.valid_scenes & current_scene == 0:
                continue
            commands = items.command
            regexs = items.regex
            if commands:
                for command in commands:
                    if command in msg and (not items.at or self.at in msg):
                        if await self.check_command(
                            objectized_data, treated_msg, items, command=command
                        ):
                            return True
            else:
                for regex in regexs:
                    regex = regex.search(msg)
                    if regex and (not items.at or self.at in msg):
                        if await self.check_command(
                            objectized_data, treated_msg, items, regex=regex
                        ):
                            return True

    @exception_processor
    async def data_process(self, data: Dict):
        # initialize values
        t = data.get("t")
        d = data.get("d", {})
        if not d:
            data["d"] = d
        data["d"]["t"] = t
        data["d"]["event_id"] = data.get("id")
        # process and distribute data
        if t in EVENTS_TO_DISPATCH:
            _key, _grp = EVENTS_TO_DISPATCH[t]
            if self.sandbox and not self.sandbox.checker(_grp, data):
                return
            await self.distribute(self.func_registers[_key], data)
        elif (
            t in EVENTS.MESSAGE_CREATE
            or t in EVENTS.DM_CREATE
            or t in EVENTS.C2C_MESSAGE_CREATE
            or t in EVENTS.GROUP_AT_MESSAGE_CREATE
        ):
            if self.msg_treat:
                raw_msg = d.get("content", "").strip()
                treated_msg = treat_msg(raw_msg, self.at)
                data["d"]["treated_msg"] = treated_msg
            else:
                treated_msg = ""
            # distribute_commands return True when short circuit
            if t in EVENTS.MESSAGE_CREATE:
                if self.sandbox and not self.sandbox.checker(
                    EVENTS_ENUM.MESSAGE_CREATE, data
                ):
                    return
                if not await self.distribute_commands(
                    CommandValidScenes.GUILD, data, treated_msg
                ):
                    await self.distribute(self.func_registers["on_msg"], data)
            elif t in EVENTS.DM_CREATE:
                if self.sandbox and not self.sandbox.checker(
                    EVENTS_ENUM.DM_CREATE, data
                ):
                    return
                if not await self.distribute_commands(
                    CommandValidScenes.DM, data, treated_msg
                ):
                    await self.distribute(self.func_registers["on_dm"], data)
            elif t in EVENTS.C2C_MESSAGE_CREATE:
                if self.sandbox and not self.sandbox.checker(
                    EVENTS_ENUM.C2C_MESSAGE_CREATE, data
                ):
                    return
                if not await self.distribute_commands(
                    CommandValidScenes.C2C, data, treated_msg
                ):
                    await self.distribute(self.func_registers["on_friend_msg"], data)
            else:  # t in EVENTS.GROUP_AT_MESSAGE_CREATE
                if self.sandbox and not self.sandbox.checker(
                    EVENTS_ENUM.GROUP_AT_MESSAGE_CREATE, data
                ):
                    return
                if not await self.distribute_commands(
                    CommandValidScenes.GROUP, data, treated_msg
                ):
                    await self.distribute(self.func_registers["on_group_msg"], data)
        elif t in EVENTS.MESSAGE_DELETE:
            if self.sandbox and not self.sandbox.checker(
                EVENTS_ENUM.MESSAGE_DELETE, data
            ):
                return
            if self.func_registers["del_is_filter_self"]:
                target = d.get("message", {}).get("author", {}).get("id")
                op_user = d.get("op_user", {}).get("id")
                if op_user == target:
                    return
            await self.distribute(self.func_registers["on_delete"], data)
        elif t in EVENTS.FORUM:
            if self.sandbox and not self.sandbox.checker(EVENTS_ENUM.FORUM, data):
                return
            if t == "FORUM_THREAD_CREATE":
                treat_thread(data)
            await self.distribute(self.func_registers["on_forum"], data)
        else:
            self.logger.warning(f"unknown event type: [{t}]")

    async def dispatch_events(self, data: dict):
        if "s" in data:
            self.s = data["s"]
        op = data.get("op")

        if op == 11:
            self.logger.debug("心跳发送成功")
        elif op == 9:
            self.logger.error(
                "[错误] op9参数出错（一般此报错为传递了无权限的事件订阅，请检查是否有权限订阅相关事件）"
            )
            await self.protocol.close()
            await self.protocol.force_reset()
        elif op == 10:
            self.protocol.update_hearbeat_time(
                int(data.get("d", {}).get("heartbeat_interval", 40)) * 0.001
            )
            if not self.is_reconnect:
                await self.protocol.send_connect()
            else:
                await self.protocol.send_reconnect()
        elif op == 0:
            # check for connection opened but not recv msg except hb
            self.protocol.update_last_msg_recv_time()

            t = data.get("t")
            if t == "READY":
                self.session_id = data.get("d", {}).get("session_id")
                self.reconnect_times = 0
                self.protocol.start_heartbeat()
                self.seq_cache.clear()
                self.logger.info("连接成功，机器人开始运行")
                if not self.is_first_run:
                    await self._start_event()
            elif t == "RESUMED":
                self.reconnect_times = 0
                self.protocol.start_heartbeat()
                self.seq_cache.clear()
                self.logger.info("重连成功，机器人继续运行")
            else:
                if "s" in data and not self.seq_cache.add_with_checking(data["s"]):
                    return
                await self.data_process(data)
        elif op == 7:  # resume
            pass
        else:
            self.logger.debug(f"未知的op类型：{op}")

    async def start(self):
        self.running = True
        self.session_manager.start(self.loop)
        await self.protocol.start()

    async def close(self):
        await self.protocol.close()

    async def stop(self):
        self.running = False
        await self.protocol.stop()
