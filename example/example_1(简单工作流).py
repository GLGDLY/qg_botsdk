# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 最简单的工作流，使用logger的一个简单实例
from qg_botsdk import BOT, Model


def deliver(data: Model.MESSAGE):
    bot.logger.info("收到消息啦！")
    if "你好" in data.treated_msg:
        # SDK版本 >= v2.4.0 可直接使用reply()
        data.reply(content="你好，世界")
        bot.logger.info(f"发送消息【你好，世界】到子频道{data.channel_id}")


if __name__ == "__main__":
    bot = BOT(bot_id="", bot_token="", is_private=True, is_sandbox=True)
    bot.bind_msg(deliver, treated_data=True)
    bot.start()
