#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 远程配置Webhook后，本地进行连接的例程（服务器端）
from qg_botsdk import BOT, Proto

if __name__ == "__main__":
    bot = BOT(
        bot_id="",
        bot_secret="",
        is_private=True,
        is_sandbox=True,
        protocol=Proto.webhook(
            path_to_ssl_cert=None,  # 当使用nginx等反向代理时，可填入None；当传入了证书时，会接受https请求
            path_to_ssl_cert_key=None,  # 当使用nginx等反向代理时，可填入None；当传入了证书时，会接受https请求
            port=8080,  # webhook挂载的端口
            path="/webhook",  # webhook挂载的路径
        ),
    )
    # 如使用Nginx等反代，需注意后端会使用以下几个路径，请注意配置：
    # (ip:port){你配置的webhook挂载路径}
    # (ip:port)/qg_botsdk/*
    # (ip:port)/qg_botsdk_remote/*

    bot.start()
