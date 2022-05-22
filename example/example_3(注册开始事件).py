# !/usr/bin/env python3
# encoding: utf-8
# 使用register_start_event，机器人开始运行时，获取机器人所在的全部频道信息、全部成员信息、频道身份组列表的一个简单实例
from qg_botsdk.qg_bot import BOT
from qg_botsdk.model import Model


def on_start():
    gbi = bot.get_bot_info()
    print(gbi.__doc__)
    all_guilds = bot.get_bot_guilds().data
    bot.logger.info('全部频道：' + str([items.name + '(' + items.id + ')' for items in all_guilds]))
    bot.logger.info('全部频道数量：' + str(len(all_guilds)))
    for items in all_guilds:
        gi = bot.get_guild_info(items.id)
        if not gi.result and gi.data.code == 11292:
            bot.logger.warning(items.name + '(' + items.id + ')[权限不足，无法查询此频道信息]')
        else:
            bot.logger.info(f'频道 {items.name}({items.id}) 的拥有者：' + str(items.owner_id))
            gm = bot.get_guild_members(items.id)
            if not all(gm.result):
                bot.logger.warning(items.name + '(' + items.id + ')[权限不足，无法查询此频道信息]')
                bot.create_permission_demand(items.id, 'xxx', 'get_guild_members', '查看成员权限')
            else:
                bot.logger.info(f'频道 {items.name}({items.id}) 的成员：' +
                                '、'.join([gm_data.nick for gm_data in gm.data]))
            gr = bot.get_guild_roles(items.id)
            if not gr.result:
                bot.logger.warning(items.name + '(' + items.id + ')[权限不足，无法查询此频道信息]')
                bot.create_permission_demand(items.id, 'xxx', 'get_guild_roles', '查看成员权限')
            else:
                bot.logger.info(f'频道 {items.name}({items.id}) 身份组：' +
                                '、'.join([f'{gr_data.name}（id:{gr_data.id}）' for gr_data in gr.data.roles]))


def deliver(data: Model.MESSAGE):
    if '你好' in data.treated_msg:
        bot.send_msg(data.channel_id, '你好，世界', message_id=data.id)


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', is_private=True, is_sandbox=True, max_shard=1)
    bot.bind_msg(deliver, treated_data=True)
    bot.register_start_event(on_start)
    bot.start()
