#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 使用register_start_event和register_stop_event，在机器人启动和关闭时执行特定操作
from qg_botsdk import BOT, Model
import time


def on_start():
    """机器人启动时执行的函数"""
    bot.logger.info("机器人已成功启动")
    gbi = bot.api.get_bot_info()
    bot.logger.info(f"机器人信息: {gbi}")

    # 获取机器人所在的频道信息
    all_guilds = bot.api.get_bot_guilds().data
    bot.logger.info(
        "全部频道：" + str([items.name + "(" + items.id + ")" for items in all_guilds])
    )
    bot.logger.info("全部频道数量：" + str(len(all_guilds)))


def on_stop():
    """机器人关闭时执行的函数"""
    bot.logger.info("机器人即将关闭")
    bot.logger.info("正在保存状态...")
    time.sleep(1)  # 模拟保存状态的操作
    bot.logger.info("状态已保存，机器人关闭完成")


def deliver(data: Model.MESSAGE):
    """处理消息的函数"""
    # 如果收到 "bye" 消息，则关闭机器人
    if data.treated_msg == "bye":
        bot.api.send_msg(data.channel_id, "机器人即将关闭，再见！")
        bot.close()
    else:
        bot.api.send_msg(data.channel_id, f"你发送了: {data.treated_msg}")


if __name__ == "__main__":
    bot = BOT(bot_id="", bot_token="", is_private=True, is_sandbox=True)
    bot.bind_msg(deliver, treated_data=True)
    bot.register_start_event(on_start)
    bot.register_stop_event(on_stop)
    bot.start()
