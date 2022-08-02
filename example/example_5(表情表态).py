# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 监听表情表态事件一个简单实例

from qg_botsdk import BOT, Model


def deliver(data: Model.MESSAGE):
    bot.logger.info('收到消息啦！')
    if '你好' in data.treated_msg:
        bot.api.send_msg(data.channel_id, '你好，世界', message_id=data.id)


def reaction(data: Model.REACTION):
    if data.t == 'MESSAGE_REACTION_ADD':
        bot.api.send_msg(data.channel_id,
                         '%s 在 [频道 %s 子频道 %s] 新增了新的表情动态！' % (data.user_id, data.guild_id, data.channel_id),
                         event_id=data.event_id)


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', is_private=True, is_sandbox=True)
    bot.bind_msg(deliver, treated_data=True)
    bot.bind_reaction(reaction)
    bot.start()
