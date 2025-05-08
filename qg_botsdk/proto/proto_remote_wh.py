#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import ssl
from asyncio import AbstractEventLoop, Future, sleep
from typing import Coroutine

import certifi
from aiohttp import ClientSession, TCPConnector, WSMsgType

from .._exception import IdTokenError
from .._utils import exception_handler
from ..async_api import AsyncAPI
from ..logger import Logger
from .abc_proto import AbstractProto
from .wh_backend import SigningKey


class RemoteWebHook(AbstractProto):
    def __init__(
        self,
        raw_api: AsyncAPI,
        intents: int,
        auth: str,
        logger: Logger,
        loop: AbstractEventLoop,
        dispatch_func: Coroutine,
        ws_url: str,
    ):
        self.raw_api = raw_api
        self.bot_id: str = self.raw_api._session._bot_id
        self.bot_secret: str = self.raw_api._session._bot_secret

        if not self.bot_secret:
            raise IdTokenError("选择 WebHook 作为协议时，必须提供 bot_secret")
        sign_key = SigningKey.from_seed(self.bot_secret.encode("ascii"))
        sign = sign_key.sign(self.bot_id.encode("ascii")).hex()
        remote_auth = "?sign=" + sign

        self.auth = auth
        self.logger = logger
        self.loop = loop
        self.dispatch_events = dispatch_func

        if not ws_url.startswith("ws://") and not ws_url.startswith("wss://"):
            raise ValueError("远程WebHook的URL必须以ws://或wss://开头")
        match_grp = re.match(r"(wss?://[^/]+)", ws_url)
        if not match_grp:
            raise ValueError("远程WebHook的URL必须包含主机名")
        self.ws_url = match_grp.group(1)
        self.http_url = self.ws_url.replace("ws://", "http://").replace(
            "wss://", "https://"
        )
        self.http_url = (
            f"{self.http_url}/qg_botsdk_remote/{self.bot_id}/ping" + remote_auth
        )
        self.ws_url = f"{self.ws_url}/qg_botsdk_remote/{self.bot_id}" + remote_auth

        self.running = True
        self.ws = None

    async def simple_ws_connect(self):
        async with ClientSession(
            connector=TCPConnector(
                ssl=ssl.create_default_context(cafile=certifi.where())
            )
        ) as ws_session:
            try:
                async with ws_session.get(
                    self.http_url, headers={"Cache-Control": "no-cache"}
                ) as resp:
                    if resp.status != 200:
                        self.logger.error(
                            f"远程WebHook后端返回状态码{resp.status}{resp.reason}，无法连接"
                        )
                        await sleep(2)
                        return
            except Exception as e:
                self.logger.error(f"无法连接到远程WebHook后端，错误：{repr(e)}")
                self.logger.error(exception_handler(e))
                await sleep(2)
                return
            async with ws_session.ws_connect(self.ws_url) as self.ws:
                self.logger.info("已链接到远程WebHook后端")
                async for msg in self.ws:
                    if msg.type == WSMsgType.TEXT:
                        try:
                            data = msg.json()
                            self.loop.create_task(self.dispatch_events(data))
                        except json.JSONDecodeError:
                            pass
                    elif msg.type in (
                        WSMsgType.CLOSE,
                        WSMsgType.CLOSED,
                        WSMsgType.ERROR,
                    ):
                        if self.running:
                            self.logger.warning(
                                "远程WebHook后端链接已断开，正在尝试重连……"
                            )
                            return
                    if not self.running:
                        return

    async def start(self):
        self.running = True
        while self.running:
            try:
                await self.simple_ws_connect()
            except Exception as e:
                self.logger.warning("远程WebHook后端链接已断开，正在尝试重连……")
                self.logger.error(repr(e))
                self.logger.error(exception_handler(e))
            finally:
                if self.ws and not self.ws.closed:
                    await self.ws.close()
            await sleep(0.1)

    async def force_reset(self):
        pass

    async def close(self):
        if self.ws and isinstance(self.ws._waiting, Future):
            self.ws._waiting.cancel()
        await self.ws.close()

    async def stop(self):
        self.running = False
        await self.close()
        self.logger.info("远程WebHook服务已结束")
