#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 使用创建身份组API、使用私信API的一个简单实例
from qg_botsdk import BOT, Model


def deliver(data: Model.MESSAGE):
    if "创建我的身份组" in data.treated_msg:
        cr = bot.api.create_role(
            data.guild_id,
            name=f"{data.author.username}的身份组",
            color="#019F86",
            hoist=True,
        )
        if cr.result:
            # SDK版本 >= v2.4.0 可直接使用reply()
            data.reply(f"【{data.author.username}的身份组】（id:{cr.data.role_id}）已经被创建好啦！")
    elif "私信我" in data.treated_msg:
        cdg = bot.api.create_dm_guild(data.author.id, data.guild_id)
        if cdg.result:
            bot.api.send_dm(
                cdg.data.guild_id,
                "这是我跟您的专属私信频道，嘘……不要告诉其他人哦~",
                message_id=data.id,
            )
        else:
            bot.api.send_embed(
                data.channel_id,
                title="创建失败！",
                content=[f"错误码：{cdg.data.code}（信息：{cdg.data.message}）"],
                message_id=data.id,
            )


def deliver_dm(data: Model.DIRECT_MESSAGE):
    if "给爷笑一个" in data.treated_msg:
        # SDK版本 >= v2.4.0 可直接使用reply()
        data.reply("嘿嘿~", message_reference_id=data.id)


if __name__ == "__main__":
    bot = BOT(bot_id="", bot_token="", is_private=True, is_sandbox=False)
    bot.bind_msg(deliver, treated_data=True)
    bot.bind_dm(deliver_dm)
    bot.start()
