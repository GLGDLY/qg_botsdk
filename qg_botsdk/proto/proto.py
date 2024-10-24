#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from asyncio import AbstractEventLoop
from enum import IntEnum
from typing import Any, Coroutine, Optional

from ..async_api import AsyncAPI
from ..logger import Logger
from .abc_proto import AbstractProto
from .proto_wh import WebHook
from .proto_ws import WS


class ProtoType(IntEnum):
    WebSocket = 0
    WebHook = 1


class Proto:
    def __init__(self, proto_type: ProtoType, **kwargs: Any):
        self.proto: AbstractProto
        if proto_type == ProtoType.WebSocket:
            self.proto = WS
        elif proto_type == ProtoType.WebHook:
            self.proto = WebHook
        else:
            raise ValueError("Invalid ProtoType")
        self.kwargs = kwargs

    def __call__(
        self,
        raw_api: AsyncAPI,
        intents: int,
        auth: str,
        logger: Logger,
        loop: AbstractEventLoop,
        dispatch_func: Coroutine,
    ) -> AbstractProto:
        return self.proto(
            raw_api=raw_api,
            intents=intents,
            auth=auth,
            logger=logger,
            loop=loop,
            dispatch_func=dispatch_func,
            **self.kwargs
        )

    @classmethod
    def websocket(
        cls,
        shard_no: int = 0,
        total_shard: int = 1,
        disable_reconnect_on_not_recv_msg: float = 1000,
    ) -> "Proto":
        """
        使用 WebSocket 作为协议

        :param shard_no: 当前分片数，如不熟悉相关配置请不要轻易改动此项，默认0
        :param total_shard: 最大分片数，如不熟悉相关配置请不要轻易改动此项，默认1
        :param disable_reconnect_on_not_recv_msg: 当机器人长时间未收到消息后进行连接而非重连。默认1000秒
        """
        return cls(
            ProtoType.WebSocket,
            shard_no=shard_no,
            total_shard=total_shard,
            disable_reconnect_on_not_recv_msg=disable_reconnect_on_not_recv_msg,
        )

    @classmethod
    def webhook(
        cls,
        path_to_ssl_cert: Optional[str],
        path_to_ssl_cert_key: Optional[str],
        port: int,
        path: str = "/",
    ) -> "Proto":
        """
        使用 WebHook 作为协议

        :param path_to_ssl_cert: SSL证书路径，如使用了如nginx等反向代理方法处理https，可填None
        :param path_to_ssl_cert_key: SSL证书密钥路径，如使用了如nginx等反向代理方法处理https，可填None
        :param port: webhook挂载的本机端口
        :param path: webhook挂载的路径，默认为根路径
        """
        return cls(
            ProtoType.WebHook,
            path_to_ssl_cert=path_to_ssl_cert,
            path_to_ssl_cert_key=path_to_ssl_cert_key,
            port=port,
            path=path,
        )
