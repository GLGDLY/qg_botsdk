# encoding: utf-8
# 使用register_start_event，机器人开始运行时，获取机器人所在的全部频道信息的一个简单实例
# 使用主动消息、logger的一个简单实例
from qg_botsdk.qg_bot import BOT
from qg_botsdk.model import *


def on_start():
    all_guilds = bot.get_me_guilds()
    bot.logger.info('全部频道：' + str([items['name'] + '(' + items['id'] + ')' for items in all_guilds]))
    bot.logger.info('全部频道数量：' + str(len(all_guilds)))
    for items in all_guilds:
        gi = bot.get_guild_info(items["id"])
        if 'code' in gi and str(gi['code']) == '11292':
            bot.logger.warning(items['name'] + '(' + items['id'] + ')[权限不足，无法查询此频道信息]')
        else:
            bot.logger.info(f'频道 {items["name"]}({items["id"]}) 的拥有者：' + str(items['owner_id']))
    bot.send_msg('这是主动消息', msg_id=None, channel='1998372')


def deliver(data: MESSAGE):
    if '你好' in data.treated_msg:
        bot.send_msg('你好，世界', str(data.id), str(data.channel_id))


def msg_audit(data: MESSAGE_AUDIT):
    """
    只有审核通过事件才会有message_id的值
    """
    bot.logger.info('主动消息审核通过啦，已自动发往子频道%s了！' % data.channel_id)


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', is_private=True, is_sandbox=True, max_shard=1)
    bot.bind_msg(deliver, treated_data=True)
    bot.bind_audit(msg_audit)
    bot.register_start_event(on_start)
    bot.start()
