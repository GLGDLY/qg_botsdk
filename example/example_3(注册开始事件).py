#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 使用register_start_event，机器人开始运行时，获取机器人所在的全部频道信息、全部成员信息、频道身份组列表的一个简单实例
from qg_botsdk import BOT, Model


def on_start():
    gbi = bot.api.get_bot_info()
    # 目前 print(gbi) 和 print(gbi.__doc__) 已可输出相同结果
    print(gbi)
    print(gbi.__doc__)
    all_guilds = bot.api.get_bot_guilds().data
    bot.logger.info(
        "全部频道：" + str([items.name + "(" + items.id + ")" for items in all_guilds])
    )
    bot.logger.info("全部频道数量：" + str(len(all_guilds)))
    for items in all_guilds:
        gi = bot.api.get_guild_info(items.id)
        if not gi.result and gi.data.code == 11292:
            bot.logger.warning(
                items.name + "(" + items.id + ")[权限不足，无法查询此频道信息]"
            )
        else:
            bot.logger.info(
                f"频道 {items.name}({items.id}) 的拥有者：" + str(items.owner_id)
            )
            gm = bot.api.get_guild_members(items.id)
            if not all(gm.result):
                bot.logger.warning(
                    items.name + "(" + items.id + ")[权限不足，无法查询此频道信息]"
                )
                bot.api.create_permission_demand(
                    items.id, "xxx", "get_guild_members", "查看成员权限"
                )
            else:
                bot.logger.info(
                    f"频道 {items.name}({items.id}) 的成员："
                    + "、".join([gm_data.nick for gm_data in gm.data])
                )
                bot.logger.info(
                    f"频道 {items.name}({items.id}) 的成员数量：{len(gm.data)}"
                )
            gr = bot.api.get_guild_roles(items.id)
            if not gr.result:
                bot.logger.warning(
                    items.name + "(" + items.id + ")[权限不足，无法查询此频道信息]"
                )
                bot.api.create_permission_demand(
                    items.id, "xxx", "get_guild_roles", "查看成员权限"
                )
            else:
                bot.logger.info(
                    f"频道 {items.name}({items.id}) 身份组："
                    + "、".join(
                        [
                            f"{gr_data.name}（id:{gr_data.id}）"
                            for gr_data in gr.data.roles
                        ]
                    )
                )
            ggc = bot.api.get_guild_channels(items.id)
            bot.logger.info(
                f"频道 {items.name}({items.id}) 子频道："
                + "、".join(
                    [f"{gr_data.name}（id:{gr_data.id}）" for gr_data in ggc.data]
                )
            )


def deliver(data: Model.MESSAGE):
    if "你好" in data.treated_msg:
        bot.api.send_embed(
            data.channel_id,
            content=[
                "【@机器人 我的】\n查看我的资料卡",
                "【@机器人 我的】\n查看我的资料卡",
            ],
            message_id=data.id,
        )


if __name__ == "__main__":
    bot = BOT(bot_id="", bot_token="", is_private=True, is_sandbox=True)
    bot.bind_msg(deliver, treated_data=True)
    bot.register_start_event(on_start)
    bot.start()
