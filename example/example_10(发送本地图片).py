# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 发送本地图片、使用emoji的一个实例（本地图片要求SDK版本>=2.1.3，当前仅普通消息可直接上传图片，embed和ark暂无相关能力）
from qg_botsdk import BOT, Model


def deliver(data: Model.MESSAGE):
    # SDK版本 >= v2.4.0 可直接使用reply()
    if '你好' in data.treated_msg:
        data.reply('你好，世界 <emoji:106>')   # 发送QQ系统表情emoji
        data.reply('你好，世界 \U0001F600')    # 发送unicode格式的emoji
    elif '图片' in data.treated_msg:
        # 方法1（阅读档案后传入bytes类型图片数据）：
        with open('example_10_image.jpg', 'rb') as img:
            img_bytes = img.read()
            data.reply(file_image=img_bytes)
        # 方法2（打开档案后直接传入档案）：
        with open('example_10_image.jpg', 'rb') as img:
            data.reply(file_image=img)
        # 方法3（直接传入图片路径）：
        data.reply(file_image='example_10_image.jpg')


def deliver_dm(data: Model.DIRECT_MESSAGE):
    # SDK版本 >= v2.4.0 可直接使用reply()
    if '图片' in data.treated_msg:
        # 方法1（阅读档案后传入bytes类型图片数据）：
        with open('example_10_image.jpg', 'rb') as img:
            img_bytes = img.read()
            data.reply(file_image=img_bytes)
        # 方法2（打开档案后直接传入档案）：
        with open('example_10_image.jpg', 'rb') as img:
            data.reply(file_image=img)
        # 方法3（直接传入图片路径）：
        data.reply(file_image='example_10_image.jpg')


if __name__ == '__main__':
    bot = BOT(bot_id='', bot_token='', is_private=True, is_sandbox=True)
    bot.bind_msg(deliver)
    bot.bind_dm(deliver_dm)
    bot.start()
