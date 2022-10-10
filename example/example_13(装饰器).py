# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 发送装饰器的一个实例（装饰器要求SDK版本>=2.5.0）
from qg_botsdk import BOT, Model

bot = BOT(bot_id='', bot_token='', is_private=True, is_sandbox=True)


# is_short_circuit代表短路机制，即如用户输入c_0c_1，理论可触发c_0、c_1两个函数，但由于短路机制，仅会触发c_0的函数
@bot.on_command(command='c_0', is_short_circuit=True)
def c_0(data: Model.MESSAGE):
    data.reply('导入单command进行注册，用户消息包含指令c_0可触发此函数')


# is_require_at代表是否要求检测到用户@了机器人才可触发指令
@bot.on_command(command=['c_1', 'case_1'], is_short_circuit=True, is_require_at=True)
def c_1(data: Model.MESSAGE):
    data.reply('导入command列表进行注册，用户消息包含每个指令（c_1、case_1）均可触发此函数')


# is_require_admin代表是否要求检测到用户是频道主或频道管理才可触发指令
@bot.on_command(regex=r'c(?:ase)?_2', is_short_circuit=True, is_require_at=True, is_require_admin=True)
def c_2(data: Model.MESSAGE):
    data.reply('导入正则表达式进行注册，用户消息符合正则表达式即可触发此函数')
    bot.close()


# 注册常规bind_msg函数的装饰器使用方式
@bot.bind_msg()
def deliver(data: Model.MESSAGE):
    data.reply(file_image=r'example_10_image.jpg')


if __name__ == '__main__':
    bot.start()
