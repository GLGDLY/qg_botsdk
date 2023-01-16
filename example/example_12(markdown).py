#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 发送markdown消息的一个实例（markdown消息要求SDK版本>=2.3.6，需预先在平台后台申请）
from qg_botsdk import BOT, Model


def deliver(data: Model.MESSAGE):
    if "md" in data.treated_msg:
        # markdown消息中的key_values格式同时支持[{'key': 'value'}]或者[{'key': ['value']}]（value可以是list[str]或str）
        bot.api.send_markdown(
            data.channel_id,
            template_id="102012416_1660652194",
            key_values={"target_id": data.author.id, "result": ["成功"]},
            message_id=data.id,
        )
        # 另加入按钮组件的用法如下：
        bot.api.send_markdown(
            data.channel_id,
            template_id="102012416_1660652194",
            key_values={"target_id": data.author.id, "result": ["成功"]},
            keyboard_id="102012416_1660653100",
            message_id=data.id,
        )


def button(data: Model.INTERACTION):  # md按钮action type 1回调的interaction事件
    data.reply(
        f"received button interaction event, button_data: {data.data.resolved.button_data}"
    )


if __name__ == "__main__":
    bot = BOT(bot_id="", bot_token="", is_private=True, is_sandbox=True)
    bot.bind_msg(deliver)
    bot.bind_interaction(button)
    bot.start()
