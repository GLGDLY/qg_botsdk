#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 编写plugins的一个实例（plugins要求SDK版本>=2.5.1）
from qg_botsdk import Model, Plugins, Scope


@Plugins.on_command("p_0", is_short_circuit=True)
def p_0(data: Model.MESSAGE):
    data.reply("使用plugins的on_command模块进行注册，用户消息包含指令p_0可触发此函数")
    print(Plugins.api.get_bot_info())  # Plugins.api相当于BOT.api，使用时会自动将其替换成当前机器人实例里的api模块

    # session用于在不同作用域（scope）间保存和传递字典的k-v pair数据，scope可为USER、GROUP、GLOBAL
    if _session := Plugins.session.get(Scope.USER, "Plugin"):
        _session.data["status"] = "p0"
    else:
        Plugins.session.new(Scope.USER, "Plugin", {"status": "p0"})


@Plugins.on_command("p_1", is_short_circuit=True)
def p_1(data: Model.MESSAGE):
    # session用于在不同作用域（scope）间保存和传递字典的k-v pair数据，scope可为USER、GROUP、GLOBAL
    if _session := Plugins.session.get(Scope.USER, "Plugin"):
        _session.data["status"] = "p1"
    else:
        Plugins.session.new(Scope.USER, "Plugin", {"status": "p1"})
