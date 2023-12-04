#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 最简单的工作流，使用logger的一个简单实例
from qg_botsdk import BOT, ApiModel, Model


def deliver(data):
    bot.logger.info("收到消息啦！")
    if "你好" in data.treated_msg:
        bot.api.send_group_msg(data.group_openid, ApiModel.Message(content="你好，世界"))
        bot.logger.info(f"发送消息【你好，世界】到群{data.group_openid}")


if __name__ == "__main__":
    bot = BOT(
        bot_id="",
        bot_token="",
        bot_secret="",
    )
    bot.bind_group_msg(deliver)
    bot.start()
