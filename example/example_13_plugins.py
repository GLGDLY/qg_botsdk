#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 编写plugins的一个实例（plugins要求SDK版本>=2.5.1）
from qg_botsdk import Model, Plugins


@Plugins.on_command("p_0", is_short_circuit=True)
def p_0(data: Model.MESSAGE):
    data.reply("使用plugins的on_command模块进行注册，用户消息包含指令p_0可触发此函数")
    print(Plugins.api.get_bot_info())  # Plugins.api相当于BOT.api，使用时会自动将其替换成当前机器人实例里的api模块
