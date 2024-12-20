#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 远程配置Webhook后，本地进行连接的例程（本地端）
from qg_botsdk import BOT, ApiModel, Model, Proto


def deliver(data: Model.MESSAGE):
    bot.logger.info("收到消息啦！")
    if "你好" in data.treated_msg:
        data.reply("你好，世界")
        data.reply(ApiModel.Message(content="你好，世界"))
        data.reply(ApiModel.MessageEmbed(title="你好", content=["世界"]))
        bot.logger.info(f"发送消息【你好，世界】到子频道{data.channel_id}")


if __name__ == "__main__":
    bot = BOT(
        bot_id="",
        bot_secret="",
        is_private=True,
        is_sandbox=True,
        protocol=Proto.remote_webhook(
            ws_url="ws://xxx.com",  # 远程webhook挂载的url，无需添加服务端配置的回调后缀路径
        ),
    )
    # 请替换 xxx.com 为你的远程服务端域名，此处仅为示例

    bot.load_default_msg_logger()
    bot.bind_msg(deliver, treated_data=True)
    bot.start()
