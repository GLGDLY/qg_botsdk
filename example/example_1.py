# encoding: utf-8
# 最简单的工作流，使用logger的一个简单实例

from qg_bot import BOT
import logger


def deliver(json_data):
    logger.debug(json_data)
    logger.info('收到消息啦！')
    if '你好' in json_data['treated_msg']:
        bot.send_msg('你好，世界', str(json_data['d']['id']), str(json_data['d']['channel_id']))


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', is_private=True, is_sandbox=True, max_shard=1)
    bot.bind_msg(deliver, treated_data=True)
    bot.start()
