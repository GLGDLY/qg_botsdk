# encoding: utf-8
# 监听论坛事件，并获取帖子内容的一个实例
from qg_botsdk.model import *
from qg_botsdk.qg_bot import BOT


def deliver(data: MESSAGE):
    if '你好' in data.treated_msg:
        bot.send_msg('你好，世界', str(data.id), str(data.channel_id))


def forums_event(data: FORUMS_EVENT):
    """
    目前论坛事件仅能收到创建帖子的FORUM_THREAD_CREATE，回帖和回复都没有任何推送

    现有信息的type字段：
    type 1：普通文本，子字段text
    type 4：url信息，子字段url

    现无消息，根据文档列出的type：
    原type 2：at信息，目前为空子字段，无任何内容反馈
    原type 4：表情，目前为空子字段，无任何内容反馈
    原type 5：#子频道，目前为空子字段，无任何内容反馈
    原type 10：视频，目前为空子字段，无任何内容反馈
    原type 11：图片，目前为空子字段，无任何内容反馈
    """
    if data.t == 'FORUM_THREAD_CREATE':
        title = data.thread_info.title.paragraphs[0].elems[0].text.text
        content = ''
        for items in data.thread_info.content.paragraphs:
            d = items.elems[0]
            if d:
                if d.type == 1:
                    content += d.text.text
                elif d.type == 4:
                    content += f'{d.url.desc}（链接：{d.url.url}）'
        bot.logger.info(f'收到了一条新帖子！\n标题：{title}\n内容：{content}')


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', is_private=True, is_sandbox=True, max_shard=1)
    bot.bind_msg(deliver, treated_data=True)
    bot.bind_forum(forums_event)
    bot.start()
