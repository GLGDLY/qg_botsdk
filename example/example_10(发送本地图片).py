# !/usr/bin/env python3
# encoding: utf-8
# 发送本地图片的一个实例（要求SDK版本>=2.1.3，当前仅普通消息可直接上传图片，embed和ark暂无相关能力）
from qg_botsdk.model import Model
from qg_botsdk.qg_bot import BOT


def deliver(data: Model.MESSAGE):
    if '你好' in data.treated_msg:
        bot.send_msg(data.channel_id, '你好，世界', message_id=data.id)
    elif '图片' in data.treated_msg:
        # 方法1（阅读档案后传入bytes类型图片数据）：
        with open('example_10_image.jpg', 'rb') as img:
            img_bytes = img.read()
            bot.send_msg(data.channel_id, file_image=img_bytes, message_id=data.id)
        # 方法2（打开档案后直接传入档案）：
        with open('example_10_image.jpg', 'rb') as img:
            bot.send_msg(data.channel_id, file_image=img, message_id=data.id)
        # 方法3（直接传入图片路径）：
        bot.send_msg(data.channel_id, file_image='example_10_image.jpg',  message_id=data.id)
        bot.send_msg(data.channel_id, '123', message_id=data.id)


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', is_private=True, is_sandbox=True, max_shard=1)
    bot.bind_msg(deliver, treated_data=True)
    bot.start()
