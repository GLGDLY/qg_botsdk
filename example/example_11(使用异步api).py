# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 发送本地图片、使用emoji的一个实例（本地图片要求SDK版本>=2.1.3，当前仅普通消息可直接上传图片，embed和ark暂无相关能力）
from qg_botsdk import BOT, Model


async def on_start():
    # example_3 的异步版本
    gbg = await bot.api.get_bot_guilds()
    all_guilds = gbg.data
    bot.logger.info('全部频道：' + str([items.name + '(' + items.id + ')' for items in all_guilds]))
    bot.logger.info('全部频道数量：' + str(len(all_guilds)))
    for items in all_guilds:
        gi = await bot.api.get_guild_info(items.id)
        if not gi.result and gi.data.code == 11292:
            bot.logger.warning(items.name + '(' + items.id + ')[权限不足，无法查询此频道信息]')
        else:
            bot.logger.info(f'频道 {items.name}({items.id}) 的拥有者：' + str(items.owner_id))
            gm = await bot.api.get_guild_members(items.id)
            if not all(gm.result):
                bot.logger.warning(items.name + '(' + items.id + ')[权限不足，无法查询此频道信息]')
                await bot.api.create_permission_demand(items.id, 'xxx', 'get_guild_members', '查看成员权限')
            else:
                bot.logger.info(f'频道 {items.name}({items.id}) 的成员：' +
                                '、'.join([gm_data.nick for gm_data in gm.data]))
            gr = await bot.api.get_guild_roles(items.id)
            if not gr.result:
                bot.logger.warning(items.name + '(' + items.id + ')[权限不足，无法查询此频道信息]')
                await bot.api.create_permission_demand(items.id, 'xxx', 'get_guild_roles', '查看成员权限')
            else:
                bot.logger.info(f'频道 {items.name}({items.id}) 身份组：' +
                                '、'.join([f'{gr_data.name}（id:{gr_data.id}）' for gr_data in gr.data.roles]))


async def deliver(data: Model.MESSAGE):
    # example_10 的异步版本
    if '你好' in data.treated_msg:
        await bot.api.send_msg(data.channel_id, '你好，世界 <emoji:106>', message_id=data.id)  # 发送QQ系统表情emoji
        await bot.api.send_msg(data.channel_id, '你好，世界 \U0001F600', message_id=data.id)  # 发送unicode格式的emoji
    elif '图片' in data.treated_msg:
        with open('example_10_image.jpg', 'rb') as img:
            img_bytes = img.read()
            await bot.api.send_msg(data.channel_id, file_image=img_bytes, message_id=data.id)
        with open('example_10_image.jpg', 'rb') as img:
            await bot.api.send_msg(data.channel_id, file_image=img, message_id=data.id)
        await bot.api.send_msg(data.channel_id, file_image='example_10_image.jpg', message_id=data.id)

    # example_8 创建身份组模块的异步版本
    elif '创建我的身份组' in data.treated_msg:
        cr = await bot.api.create_role(data.guild_id, name=f'{data.author.username}的身份组', color='#019F86', hoist=True)
        await bot.api.create_role_member(data.author.id, data.guild_id, cr.data.role_id)
        if cr.result:
            await bot.api.send_msg(data.channel_id, f'【{data.author.username}的身份组】（id:{cr.data.role_id}）'
                                                    f'已经被创建好啦！', message_id=data.id)


async def deliver_dm(data: Model.DIRECT_MESSAGE):  # example_8 私信模块的异步版本
    if '给爷笑一个' in data.treated_msg:
        with open('example_10_image.jpg', 'rb') as img:
            img_bytes = img.read()
        await bot.api.send_dm(data.guild_id, '嘿嘿~', file_image=img_bytes, message_id=data.id)


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', is_private=True, is_sandbox=False, is_async=True)
    bot.bind_msg(deliver)
    bot.bind_dm(deliver_dm)
    bot.register_start_event(on_start)
    bot.start()
