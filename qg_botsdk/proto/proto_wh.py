#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import subprocess as sp
import sys
import time
from asyncio import AbstractEventLoop, Future, TimeoutError, sleep, wait_for
from ssl import create_default_context
from typing import Coroutine, Optional

from aiohttp import ClientSession, WSMsgType

from .._exception import IdTokenError
from .._utils import exception_handler
from ..async_api import AsyncAPI
from ..logger import Logger
from ..version import __version__
from .abc_proto import AbstractProto


class WebHook(AbstractProto):
    def __init__(
        self,
        raw_api: AsyncAPI,
        intents: int,
        auth: str,
        logger: Logger,
        loop: AbstractEventLoop,
        dispatch_func: Coroutine,
        path_to_ssl_cert: Optional[str],
        path_to_ssl_cert_key: Optional[str],
        port: int,
        path: str,
    ):
        self.raw_api = raw_api
        self.bot_id: str = self.raw_api._session._bot_id
        self.bot_secret: str = self.raw_api._session._bot_secret

        if not self.bot_secret:
            raise IdTokenError("选择 WebHook 作为协议时，必须提供 bot_secret")

        self.auth = auth
        self.logger = logger
        self.loop = loop
        self.dispatch_events = dispatch_func
        self.port = port
        self.path = path
        self.path_to_ssl_cert = path_to_ssl_cert
        self.path_to_ssl_cert_key = path_to_ssl_cert_key

        self.running = True
        self.ssl = create_default_context()
        self.ws = None

    async def check_and_start_wh_backend(self):
        # exec ./wh_backend/wh_core.py in background
        py_path = sys.executable
        file_path = os.path.abspath(__file__)
        wh_core_path = os.path.join(
            os.path.dirname(file_path), "wh_backend", "wh_core.py"
        )
        core_log = f"./log/wh_core{time.time()}.log"
        args = f"--version {__version__} --port {self.port} --log {core_log}"
        if self.path_to_ssl_cert and self.path_to_ssl_cert_key:
            args += f" --ssl_cert {self.path_to_ssl_cert} --ssl_cert_key {self.path_to_ssl_cert_key}"
        if os.name == "nt":
            # wh_core.log is locked by last process
            sp.Popen(
                f"{py_path} {wh_core_path} {args}",
                creationflags=sp.CREATE_NEW_CONSOLE,
                shell=True,
                stdout=sp.DEVNULL,
                stderr=sp.DEVNULL,
                cwd=os.curdir,
            )
        else:
            sp.Popen(
                f"{py_path} {wh_core_path} {args}",
                start_new_session=True,
                shell=True,
                stdout=sp.DEVNULL,
                stderr=sp.DEVNULL,
                cwd=os.curdir,
            )

        # wait until log is not empty to ensure wh_core is running
        async def wait_for_log():
            while not os.path.exists(core_log) or os.stat(core_log).st_size == 0:
                self.logger.warning("等待WebHook后端验证启动……")
                await sleep(1)

        try:
            await wait_for(wait_for_log(), timeout=10)
        except TimeoutError:
            self.logger.warning("WebHook后端验证启动超时")
        else:
            self.logger.info("WebHook后端已启动")

    async def simple_ws_connect(self, url, is_ssl):
        async with ClientSession() as ws_session:
            try:
                async with ws_session.head(
                    "https" + url if is_ssl else "http" + url, ssl=self.ssl
                ) as resp:
                    if resp.status != 200:
                        self.logger.error(
                            f"WebHook后端返回状态码{resp.reason}，无法连接"
                        )
                        await sleep(2)
                        return
            except Exception as e:
                self.logger.error(f"无法连接到WebHook后端，错误：{repr(e)}")
                self.logger.error(exception_handler(e))
                await sleep(2)
                return
            async with ws_session.ws_connect(
                "wss" + url if is_ssl else "ws" + url, ssl=self.ssl
            ) as self.ws:
                self.logger.info("已链接到WebHook后端")
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
                            self.logger.warning("WebHook后端链接已断开，正在尝试重连……")
                            return
                    if not self.running:
                        return

    async def start(self):
        self.running = True
        await self.check_and_start_wh_backend()
        is_ssl = self.path_to_ssl_cert and self.path_to_ssl_cert_key
        url = f"://localhost:{self.port}/qg_botsdk/{self.bot_id}?secret={self.bot_secret}&path={self.path}"
        while self.running:
            try:
                await self.simple_ws_connect(url, is_ssl)
            except Exception as e:
                self.logger.warning("WebHook后端链接已断开，正在尝试重连……")
                self.logger.error(repr(e))
                self.logger.error(exception_handler(e))
            finally:
                if self.ws and not self.ws.closed:
                    await self.ws.close()
            await sleep(0.1)

    async def close(self):
        if self.ws and isinstance(self.ws._waiting, Future):
            self.ws._waiting.cancel()
        await self.ws.close()

    async def stop(self):
        self.running = False
        await self.close()
        self.logger.info("WebHook服务已结束")
