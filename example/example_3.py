# encoding: utf-8
# 使用register_start_event，机器人开始运行时，获取机器人所在的全部频道信息的一个简单实例
# 使用logger的一个简单实例

from qg_bot import BOT
import logger


def on_start():
    all_guilds = bot.get_me_guilds()
    logger.info('全部频道：' + str([items['name'] + '(' + items['id'] + ')' for items in all_guilds]))
    logger.info('全部频道数量：' + str(len(all_guilds)))
    for items in all_guilds:
        gi = bot.get_guild_info(items["id"])
        if 'code' in gi and str(gi['code']) == '11292':
            logger.warning(items['name'] + '(' + items['id'] + ')[权限不足，无法查询此频道信息]')
        else:
            logger.info(f'频道 {items["name"]}({items["id"]}) 的拥有者：' + str(items['owner_id']))


def deliver(json_data):
    if '你好' in json_data['treated_msg']:
        bot.send_msg('你好，世界', str(json_data['d']['id']), str(json_data['d']['channel_id']))


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', is_private=True, is_sandbox=True, max_shard=1)
    bot.bind_msg(deliver, treated_data=True)
    bot.register_start_event(on_start)
    bot.start()
