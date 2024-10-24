#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 使用Webhook进行连接的最简单工作流
from qg_botsdk import BOT, ApiModel, Model, Proto


def deliver(data: Model.MESSAGE):
    bot.logger.info("收到消息啦！")
    if "你好" in data.treated_msg:
        # SDK版本 >= v2.4.0 可直接使用reply()
        data.reply("你好，世界")
        data.reply(ApiModel.Message(content="你好，世界"))
        data.reply(ApiModel.MessageEmbed(title="你好", content=["世界"]))
        bot.logger.info(f"发送消息【你好，世界】到子频道{data.channel_id}")


if __name__ == "__main__":
    bot = BOT(
        bot_id="",
        bot_token="",
        is_private=True,
        is_sandbox=True,
        protocol=Proto.webhook(
            path_to_ssl_cert=None,  # 当使用nginx等反向代理时，可填入None；当传入了证书时，会接受https请求
            path_to_ssl_cert_key=None,  # 当使用nginx等反向代理时，可填入None；当传入了证书时，会接受https请求
            port=8080,  # webhook挂载的端口
            path="/webhook",  # webhook挂载的路径
        ),
    )
    # 此例子中，Webhook会运行在 0.0.0.0:8080/webhook

    bot.load_default_msg_logger()
    bot.bind_msg(deliver, treated_data=True)
    bot.start()
