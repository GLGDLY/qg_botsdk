# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 使用获取子频道信息、创建子频道API的一个简单实例
from qg_botsdk import BOT, Model


def deliver(data: Model.MESSAGE):
    if data.treated_msg == "来个我的子频道":
        current_channel = bot.api.get_channels_info(data.channel_id)
        create_return = bot.api.create_channels(
            data.guild_id,
            f"{data.author.username}的子频道",
            0,
            current_channel.data.position + 1,
            current_channel.data.parent_id,
            0,
            2,
            [data.author.id],
            1,
        )
        if create_return.result:
            bot.logger.info("创建成功！")
        else:
            bot.logger.error(
                f"创建失败！（{create_return.data.code}: {create_return.data.message}）"
            )


if __name__ == "__main__":
    bot = BOT(bot_id="", bot_token="", is_private=True, is_sandbox=True)
    bot.bind_msg(deliver, treated_data=True)
    bot.start()
