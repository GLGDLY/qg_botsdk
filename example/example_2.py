# encoding: utf-8
# 使用腾讯内容检测接口的一个简单实例

from qg_botsdk.qg_bot import BOT
from qg_botsdk.model import *


def deliver(data: MESSAGE):
    content = data.treated_msg
    if '内容检测' in content:
        if not bot.security_check(content[content.find('内容检测') + 4:]):
            send_msg = '检测不通过，内容有违规'
        else:
            send_msg = '检测通过，内容并无违规'
        bot.send_msg(send_msg, str(data.id), str(data.channel_id))
    return


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', bot_secret='', is_private=True, is_sandbox=True, max_shard=1)
    bot.bind_msg(deliver, treated_data=True)
    bot.start()