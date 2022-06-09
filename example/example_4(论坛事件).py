# !/usr/bin/env python3
# encoding: utf-8
# 监听论坛事件并获取帖子内容，如有安全风险则自动删除的一个实例
from qg_botsdk.model import Model
from qg_botsdk.qg_bot import BOT


def deliver(data: Model.MESSAGE):
    if '你好' in data.treated_msg:
        bot.api.send_msg(data.channel_id, '你好，世界', message_id=data.id)


def forums_event(data: Model.FORUMS_EVENT):
    """
    目前论坛事件仅能收到创建帖子的FORUM_THREAD_CREATE，回帖和回复都没有任何推送

    现有信息的type字段：
    type 1：普通文本，子字段text
    type 2：图片，子字段image
    type 3：视频，子字段video
    type 4：url信息，子字段url

    现无消息，根据文档列出的type：
    原type 2：at信息，目前为空子字段，无任何内容反馈
    原type 4：表情，目前为空子字段，无任何内容反馈
    原type 5：#子频道，目前为空子字段，无任何内容反馈
    """
    print(data.__doc__)   # 可借此获取json格式的实际数据结构
    if data.t == 'FORUM_THREAD_CREATE':
        title = data.thread_info.title.paragraphs[0].elems[0].text.text
        content = ''
        for items in data.thread_info.content.paragraphs:
            d = items.elems[0]
            if 'type' in d.__dict__:
                if d.type == 1:
                    content += d.text.text
                elif d.type == 4:
                    content += f'{d.url.desc}（链接：{d.url.url}）'
        bot.logger.info(f'收到了一条新帖子！\n标题：{title}\n内容：{content}')
        if not bot.api.security_check(content):
            # 删除帖子接口疑似存在官方bug，503013：thread_id is invalid
            dt = bot.api.delete_thread(data.channel_id, data.thread_info.thread_id)
            if not dt.result:
                bot.logger.warning(f'上述帖子内容存在风险，但机器人无法自动删除（{dt.data.code}：{dt.data.message}）')
            else:
                bot.logger.info('上述帖子内容存在风险，机器人已自动删除相关内容')


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', bot_secret='', is_private=True, is_sandbox=True, max_shard=1)
    bot.bind_msg(deliver, treated_data=True)
    bot.bind_forum(forums_event)
    bot.start()
