#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ssl
from asyncio import AbstractEventLoop, CancelledError, Future
from asyncio import TimeoutError as AsyncTimeoutError
from asyncio import sleep
from json import JSONDecodeError, dumps
from time import time
from typing import Coroutine

import certifi
from aiohttp import ClientSession, TCPConnector, WSMsgType, WSServerHandshakeError

from .._exception import IdTokenError
from .._utils import exception_handler
from ..async_api import AsyncAPI
from ..logger import Logger
from .abc_proto import AbstractProto

Op9RetryTime = 3


class WS(AbstractProto):
    def __init__(
        self,
        raw_api: AsyncAPI,
        intents: int,
        auth: str,
        logger: Logger,
        loop: AbstractEventLoop,
        dispatch_func: Coroutine,
        shard_no: int,
        total_shard: int,
        disable_reconnect_on_not_recv_msg: int,
    ):
        self.raw_api = raw_api
        self.auth = auth
        self.ws_url = None
        self.logger = logger
        self.loop = loop
        self.intents = intents
        self.shard_no = shard_no
        self.total_shard = total_shard
        self.disable_reconnect_on_not_recv_msg = disable_reconnect_on_not_recv_msg
        self.ws = None
        self.running = True
        self.is_reconnect = False
        self.reconnect_times = 0
        self.heartbeat = None
        self.disable_reconnect = False
        self.skip_connect_waiting = False
        self.s = None
        self.session_id = None
        self.dispatch_events = dispatch_func

        self.last_msg_recv_time = time()

    def update_last_msg_recv_time(self):
        self.last_msg_recv_time = time()

    def update_hearbeat_time(self, time: float):
        self.heartbeat_time = time

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
        if self.heartbeat is None:
            self.heartbeat = self.loop.create_task(self.heart())

    async def connect(self):
        self.reconnect_times += 1
        try:
            async with ClientSession(
                connector=TCPConnector(
                    ssl=ssl.create_default_context(cafile=certifi.where())
                )
            ) as ws_session:
                async with ws_session.ws_connect(self.ws_url) as self.ws:
                    while not self.ws.closed:
                        try:
                            message = await self.ws.receive(
                                timeout=self.disable_reconnect_on_not_recv_msg
                            )
                        except (AsyncTimeoutError, CancelledError):
                            self.logger.warning("BOT_WS链接已断开，正在尝试重连……")
                            self.disable_reconnect = True
                            self.skip_connect_waiting = True
                            return
                        if not self.running:
                            return
                        if message.type == WSMsgType.TEXT:
                            try:
                                data = message.json()
                                self.loop.create_task(self.dispatch_events(data))
                            except JSONDecodeError:
                                pass
                        elif message.type in (
                            WSMsgType.CLOSE,
                            WSMsgType.CLOSED,
                            WSMsgType.ERROR,
                        ):
                            if self.running:
                                self.is_reconnect = True
                                self.logger.warning("BOT_WS链接已断开，正在尝试重连……")
                                return
                        if (
                            time() - self.last_msg_recv_time
                            > self.disable_reconnect_on_not_recv_msg
                        ):
                            self.disable_reconnect = True
                            self.skip_connect_waiting = True
                            self.update_last_msg_recv_time()
                            self.logger.warning(
                                "BOT_WS链接已因长时间未收到消息而主动断开"
                            )
                            return
        except Exception as e:
            self.logger.warning("BOT_WS链接已断开，正在尝试重连……")
            self.logger.error(repr(e))
            self.logger.error(exception_handler(e))
            return
        finally:
            if self.heartbeat is not None and not self.heartbeat.cancelled():
                self.heartbeat.cancel()
                self.heartbeat = None
            if self.ws and not self.ws.closed:
                await self.ws.close()

    async def get_ws_url(self):
        gateway = await self.raw_api._session.get(
            f"{self.raw_api._bot_url}/gateway/bot"
        )
        gateway = await gateway.json()
        self.ws_url = gateway.get("url")
        if not self.ws_url:
            raise IdTokenError(
                "你输入的 bot_id 和/或 bot_token 错误，无法连接使用机器人\n如尚未有相关票据，"
                "请参阅 https://qg-botsdk.readthedocs.io/zh_CN/latest/quick_start 了解相关详情"
            )
        self.logger.debug("[机器人ws地址] " + self.ws_url)

    async def start(self):
        self.running = True
        await self.get_ws_url()

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
            await sleep(0.1)
            self.is_reconnect = self.reconnect_times < 20

    async def close(self):
        if self.ws and isinstance(self.ws._waiting, Future):
            self.ws._waiting.cancel()
        await self.ws.close()

    async def stop(self):
        self.running = False
        await self.close()
        self.logger.info("WebSocket 服务已结束")
