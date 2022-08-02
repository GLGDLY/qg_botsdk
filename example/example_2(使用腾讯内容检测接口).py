# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 使用腾讯内容检测接口的一个简单实例

from qg_botsdk import BOT, Model


def deliver(data: Model.MESSAGE):
    content = data.content
    if '内容检测' in content:
        if not bot.api.security_check(content[content.find('内容检测') + 4:]):
            send_msg = '检测不通过，内容有违规'
        else:
            send_msg = '检测通过，内容并无违规'
        bot.api.send_msg(data.channel_id, send_msg, message_id=data.id)
    return


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', bot_secret='', is_private=True, is_sandbox=True)
    bot.bind_msg(deliver, treated_data=True)
    bot.start()
