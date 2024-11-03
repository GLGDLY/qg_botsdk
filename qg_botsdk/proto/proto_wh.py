#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from asyncio import AbstractEventLoop, sleep
from json import dumps, loads
from ssl import Purpose, create_default_context
from typing import Coroutine, Optional

from aiohttp import web

from .._exception import IdTokenError
from .._utils import exception_handler
from ..async_api import AsyncAPI
from ..ed25519 import SigningKey
from ..logger import Logger
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
        self.auth = auth
        self.logger = logger
        self.loop = loop
        self.dispatch_events = dispatch_func
        self.port = port
        self.path = path

        self.running = True

        self.bot_id: str = self.raw_api._session._bot_id
        self.bot_secret: str = self.raw_api._session._bot_secret

        if path_to_ssl_cert and path_to_ssl_cert_key:
            self.ssl = create_default_context(Purpose.CLIENT_AUTH)
            self.ssl.check_hostname = False
            self.ssl.load_cert_chain(path_to_ssl_cert, path_to_ssl_cert_key)
        else:
            self.ssl = None

        app = web.Application()
        app.router.add_post(self.path, self.handler)
        self.runner = web.AppRunner(app)

    def validation(self, data: dict):
        if not self.bot_secret:
            raise IdTokenError("选择 WebHook 作为协议时，必须提供 bot_secret")
        sign_key = SigningKey.from_seed(self.bot_secret.encode("ascii"))
        msg: str = data.get("event_ts") + data.get("plain_token")
        signature = sign_key.sign(msg.encode("ascii")).hex()
        return dumps(
            {
                "plain_token": data.get("plain_token"),
                "signature": signature,
            }
        )

    async def handler(self, request: web.Request):
        if (
            request.headers.get("User-Agent") != "QQBot-Callback"
            or request.headers.get("X-Bot-Appid") != f"{self.bot_id}"
        ):
            return web.Response(status=403)
        try:
            body = await request.json()
            if isinstance(body, str):
                payload = loads(body)
            else:
                payload = body
            if payload.get("op") == 13:
                return web.Response(status=200, body=self.validation(payload.get("d")))
            else:
                self.loop.create_task(self.dispatch_events(payload))
                return web.Response(status=200)
        except Exception as e:
            self.logger.error(e.__repr__())
            self.logger.debug(exception_handler(e))
            return web.Response(status=400)

    async def start(self):
        self.running = True
        while self.running:
            try:
                await self.runner.setup()
                site = web.TCPSite(self.runner, port=self.port, ssl_context=self.ssl)
                self.logger.info(
                    f"WebHook 服务已在 0.0.0.0:{self.port}{self.path} 启动"
                )
                await site.start()
                await site._server.serve_forever()
            except Exception as e:
                self.logger.error(e.__repr__())
                self.logger.debug(exception_handler(e))
                await self.runner.cleanup()
                continue
            await self.runner.cleanup()
            await sleep(1)

    async def close(self):
        await self.runner.cleanup()

    async def stop(self):
        self.running = False
        await self.close()
        self.logger.info("WebHook 服务已结束")
