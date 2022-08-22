# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 监听表情表态事件一个简单实例

from qg_botsdk import BOT, Model


def deliver(data: Model.MESSAGE):
    bot.logger.info('收到消息啦！')
    if '你好' in data.treated_msg:
        # SDK版本 >= v2.4.0 可直接使用reply()
        data.reply('你好，世界')


def reaction(data: Model.REACTION):
    if data.t == 'MESSAGE_REACTION_ADD':
        # SDK版本 >= v2.4.0 可直接使用reply()
        msg = '%s 在 [频道 %s 子频道 %s] 新增了新的表情动态！' % (data.user_id, data.guild_id, data.channel_id)
        data.reply(msg)


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', is_private=True, is_sandbox=True)
    bot.bind_msg(deliver, treated_data=True)
    bot.bind_reaction(reaction)
    bot.start()
