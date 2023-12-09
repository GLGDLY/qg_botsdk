#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from asyncio import AbstractEventLoop
from asyncio import TimeoutError as AsyncTimeoutError
from asyncio import all_tasks, sleep
from concurrent.futures import ThreadPoolExecutor
from copy import copy, deepcopy
from json import dumps, loads
from ssl import create_default_context
from typing import Any, Callable, Dict, List, Union

from aiohttp import ClientSession, WSMsgType, WSServerHandshakeError

from ._api_model import StrPtr
from ._session import SessionManager
from ._statics import EVENTS
from ._utils import (
    exception_handler,
    exception_processor,
    object_class,
    objectize,
    treat_msg,
    treat_thread,
)
from .api import API
from .async_api import AsyncAPI
from .http import Session
from .logger import Logger
from .model import BotCommandObject, Model

Op9RetryTime = 2


class BotWs:
    def __init__(
        self,
        bot_id: str,
        bot_token: str,
        bot_secret: str,
        loop: AbstractEventLoop,
        http_session: Session,
        logger: Logger,
        total_shard: int,
        shard_no: int,
        ws_url: str,
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
        preprocessors: List[Callable[[Model.MESSAGE], Any]],
        disable_reconnect_on_not_recv_msg: float,
        session_manager: SessionManager,
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
        self.http_session = http_session
        self._ssl = create_default_context()
        self.logger = logger
        self.total_shard = total_shard
        self.shard_no = shard_no
        self.ws_url = ws_url
        self.auth = access_token if bot_secret else f"Bot {bot_id}.{bot_token}"
        self.on_start_function = on_start_function
        self.check_interval = check_interval
        self.repeat_function = repeat_function
        self.func_registers = func_registers
        if not intents:
            self.logger.warning("当前未订阅任何事件，将无法接收任何消息，只能使用主动消息功能")
            intents = 1
        self.intents = intents
        self.msg_treat = msg_treat
        self.dm_treat = dm_treat
        self.robot = None
        self.heartbeat_time = 0
        self.loop = loop
        self.s = None
        self.reconnect_times = 0
        self.is_reconnect = False
        self.running = True
        self.session_id = 0
        self.is_first_run = False
        self.heartbeat = None
        self.is_async = is_async
        self.events = {
            **dict(zip(EVENTS.GUILD, ["on_guild_event"] * len(EVENTS.GUILD))),
            **dict(zip(EVENTS.CHANNEL, ["on_channel_event"] * len(EVENTS.CHANNEL))),
            **dict(
                zip(
                    EVENTS.GUILD_MEMBER,
                    ["on_guild_member"] * len(EVENTS.GUILD_MEMBER),
                )
            ),
            **dict(zip(EVENTS.REACTION, ["on_reaction"] * len(EVENTS.REACTION))),
            **dict(
                zip(
                    EVENTS.INTERACTION,
                    ["on_interaction"] * len(EVENTS.INTERACTION),
                )
            ),
            **dict(zip(EVENTS.AUDIT, ["on_audit"] * len(EVENTS.AUDIT))),
            **dict(zip(EVENTS.OPEN_FORUM, ["on_open_forum"] * len(EVENTS.OPEN_FORUM))),
            **dict(zip(EVENTS.AUDIO, ["on_audio"] * len(EVENTS.AUDIO))),
            **dict(
                zip(
                    EVENTS.ALC_MEMBER,
                    ["on_live_channel_member"] * len(EVENTS.ALC_MEMBER),
                )
            ),
        }
        self.threads = ThreadPoolExecutor(max_workers) if not self.is_async else None
        self.api = api
        self.commands = commands
        self.preprocessors = preprocessors
        self.session_manager = session_manager
        self.at = "<@!%s>"
        self.disable_reconnect = False
        self.disable_reconnect_on_not_recv_msg = disable_reconnect_on_not_recv_msg
        self.skip_connect_waiting = False

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
        self.logger.info(f"机器人频道用户ID：{self.robot.id}")
        if self.on_start_function is not None:
            if self.is_async:
                self.loop.create_task(
                    self.async_start_callback_task(self.on_start_function)
                )
            else:
                self.threads.submit(self.start_callback_task, self.on_start_function)
        if self.repeat_function is not None:
            self.loop.create_task(self._time_event_check())

    async def send_connect(self):
        connect_params = {
            "op": 2,
            "d": {
                "token": self.auth,
                "intents": self.intents,
                "shard": [self.shard_no, self.total_shard],
            },
        }
        await self.ws_send(dumps(connect_params))

    async def send_reconnect(self):
        reconnect_paras = {
            "op": 6,
            "d": {"token": self.auth, "session_id": self.session_id, "seq": self.s},
        }
        await self.ws_send(dumps(reconnect_paras))

    async def ws_send(self, msg):
        if not self.ws.closed:
            await self.ws.send_str(msg)

    async def heart(self):
        heart_json = {"op": 1, "d": None}
        while self.running:
            await sleep(self.heartbeat_time)
            if not self.ws.closed:
                heart_json["d"] = self.s
                await self.ws.send_str(dumps(heart_json))

    def start_heartbeat(self):
        if self.heartbeat is None or self.heartbeat not in all_tasks():
            self.heartbeat = self.loop.create_task(self.heart())

    async def get_robot_info(self, retry=False):
        robot_info = await self.http_session.get(r"https://api.sgroup.qq.com/users/@me")
        robot_info = await robot_info.json()
        if "id" not in robot_info:
            if not retry:
                return self.get_robot_info(retry)
            else:
                self.logger.error("当前获取机器人信息失败，机器人启动失败，程序将退出运行（可重试）")
                exit()
        return objectize(robot_info)

    @exception_processor
    async def async_start_callback_task(self, func, *args):
        return await func(*args)

    @exception_processor
    def start_callback_task(self, func, *args):
        return func(*args)

    @exception_processor
    async def distribute(
        self, function, data: Dict = None, objectized_data: object_class = None
    ):
        if function:
            if not objectized_data:
                objectized_data = objectize(data.get("d", {}), self.api, self.is_async)
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
                if command
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

    def process_wait_for_commands(self, objectized_data, msg, treated_msg):
        try:
            wait_for_commands = self.session_manager.wait_for_message_checker(
                objectized_data
            )
        except Exception:
            return False
        for x in wait_for_commands:
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
        return False

    @exception_processor
    async def distribute_commands(self, data: Dict, treated_msg: str):
        objectized_data = objectize(data.get("d", {}), self.api, self.is_async)
        # run preprocessors
        for func in self.preprocessors:
            await self.distribute(func, objectized_data=objectized_data)
        # check commands
        msg = data.get("d", {}).get("content", "")
        if self.process_wait_for_commands(objectized_data, msg, treated_msg):
            return True
        for items in self.commands:
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
        # print(data)
        # initialize values
        t = data.get("t")
        d = data.get("d", {})
        if not d:
            data["d"] = d
        data["d"]["t"] = t
        data["d"]["event_id"] = data.get("id")
        # process and distribute data
        if t in self.events:
            _key = self.events[t]
            await self.distribute(self.func_registers[_key], data)
        elif (
            t in EVENTS.MESSAGE_CREATE
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
            # print("0")
            if not await self.distribute_commands(data, treated_msg):
                # print("1")
                if t in EVENTS.MESSAGE_CREATE:
                    # print("2")
                    await self.distribute(self.func_registers["on_msg"], data)
                elif t in EVENTS.C2C_MESSAGE_CREATE:
                    # print("3")
                    await self.distribute(self.func_registers["on_friend_msg"], data)
                else:  # t in EVENTS.GROUP_AT_MESSAGE_CREATE
                    # print("4")
                    await self.distribute(self.func_registers["on_group_msg"], data)
        elif t in EVENTS.MESSAGE_DELETE:
            if self.func_registers["del_is_filter_self"]:
                target = d.get("message", {}).get("author", {}).get("id")
                op_user = d.get("op_user", {}).get("id")
                if op_user == target:
                    return
            await self.distribute(self.func_registers["on_delete"], data)
        elif t in EVENTS.DM_CREATE:
            if self.dm_treat:
                raw_msg = d.get("content", "").strip()
                data["d"]["treated_msg"] = treat_msg(raw_msg, self.at)
            await self.distribute(self.func_registers["on_dm"], data)
        elif t in EVENTS.FORUM:
            treat_thread(data)
            await self.distribute(self.func_registers["on_forum"], data)
        else:
            self.logger.warning(f"unknown event type: [{t}]")

    async def dispatch_events(self, msg: str):
        data = loads(msg)
        op = data.get("op")
        if "s" in data:
            self.s = data["s"]
        if op == 11:
            self.logger.debug("心跳发送成功")
        elif op == 9:
            self.logger.error("[错误] op9参数出错（一般此报错为传递了无权限的事件订阅，请检查是否有权限订阅相关事件）")
            self.disable_reconnect = True
        elif op == 10:
            self.heartbeat_time = (
                int(data.get("d", {}).get("heartbeat_interval", 40)) * 0.001
            )
            if not self.is_reconnect:
                await self.send_connect()
            else:
                await self.send_reconnect()
        elif op == 0:
            t = data.get("t")
            if t == "READY":
                self.session_id = data.get("d", {}).get("session_id")
                self.reconnect_times = 0
                self.start_heartbeat()
                self.logger.info("连接成功，机器人开始运行")
                if not self.is_first_run:
                    await self._start_event()
            elif t == "RESUMED":
                self.reconnect_times = 0
                self.start_heartbeat()
                self.logger.info("重连成功，机器人继续运行")
            else:
                await self.data_process(data)

    async def close(self):
        if self.heartbeat is not None and not self.heartbeat.cancelled():
            self.heartbeat.cancel()
        await self.ws.close()
        self.logger.info("WS链接已结束")

    async def connect(self):
        self.reconnect_times += 1
        try:
            async with ClientSession() as ws_session:
                async with ws_session.ws_connect(self.ws_url, ssl=self._ssl) as self.ws:
                    while not self.ws.closed:
                        try:
                            message = await self.ws.receive(
                                timeout=self.disable_reconnect_on_not_recv_msg
                            )
                        except AsyncTimeoutError:
                            self.logger.warning("BOT_WS链接已断开，正在尝试重连……")
                            if (
                                self.heartbeat is not None
                                and not self.heartbeat.cancelled()
                            ):
                                self.heartbeat.cancel()
                            self.disable_reconnect = True
                            self.skip_connect_waiting = True
                            return
                        if not self.running:
                            if not not self.ws.closed:
                                await self.close()
                            return
                        if message.type == WSMsgType.TEXT:
                            self.loop.create_task(self.dispatch_events(message.data))
                            if self.disable_reconnect:
                                await self.ws.close()
                                return
                        elif message.type in (
                            WSMsgType.CLOSE,
                            WSMsgType.CLOSED,
                            WSMsgType.ERROR,
                        ):
                            if self.running:
                                self.is_reconnect = True
                                if (
                                    self.heartbeat is not None
                                    and not self.heartbeat.cancelled()
                                ):
                                    self.heartbeat.cancel()
                                self.logger.warning("BOT_WS链接已断开，正在尝试重连……")
                                return
        except Exception as e:
            self.logger.warning("BOT_WS链接已断开，正在尝试重连……")
            if self.heartbeat is not None and not self.heartbeat.cancelled():
                self.heartbeat.cancel()
            self.logger.error(repr(e))
            self.logger.error(exception_handler(e))
            return

    async def starter(self):
        self.session_manager.start(self.loop)
        await self.connect()
        while self.running:
            if self.disable_reconnect:
                if not self.skip_connect_waiting:
                    await sleep(Op9RetryTime)
                self.skip_connect_waiting = False
                self.disable_reconnect = False
                self.is_reconnect = False
            try:
                await self.connect()
            except WSServerHandshakeError:
                self.logger.warning("网络连线不稳定或已断开，请检查网络链接")
            await sleep(3)
            self.is_reconnect = self.reconnect_times < 20
