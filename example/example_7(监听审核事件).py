# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 使用主动消息、监听消息审核事件的一个简单实例
from qg_botsdk import BOT, Model


def on_start():
    bot.api.send_msg(channel_id='xxx', content='这是主动消息')


def deliver(data: Model.MESSAGE):
    if '你好' in data.treated_msg:
        bot.api.send_msg(data.channel_id, '你好，世界', message_id=data.id)


def msg_audit(data: Model.MESSAGE_AUDIT):
    """
    只有审核通过事件才会有message_id的值
    """
    bot.logger.info('主动消息审核通过啦，已自动发往子频道%s了！' % data.channel_id)


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', is_private=True, is_sandbox=True)
    bot.bind_msg(deliver, treated_data=True)
    bot.bind_audit(msg_audit)
    bot.register_start_event(on_start)
    bot.start()
