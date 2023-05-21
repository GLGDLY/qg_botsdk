#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 使用session与api.wait_for的一个实例（要求SDK版本>=3.0.0）
from random import randint
from re import compile as re_compile

from qg_botsdk import BOT, BotCommandObject, Model, Scope, WaitTimeoutError

# session用于在不同作用域（scope）间保存和传递字典的k-v pair数据，scope可为USER、GROUP、GLOBAL

bot = BOT(bot_id="", bot_token="", is_private=True, is_sandbox=True)
bot.load_default_msg_logger()  # 加载默认的消息日志记录器，将在控制台输出收到的消息


# 猜数字游戏：使用session管理指令与指令间的数据传递
@bot.on_command("猜数字")
def number_game(data: Model.MESSAGE):
    # 生成一个随机数
    number = randint(0, 100)

    # 将随机数保存在session中
    bot.session.new(
        scope=Scope.USER,
        key="数字游戏",
        data={"number": number, "upper_limit": 100, "lower_limit": 0},
        timeout=60,
        timeout_reply=f"超时啦，本次猜数字游戏结束，本次答案是{number}呢",
    )  # 创建一个60秒超时的session
    # 发送提示信息
    data.reply(f"已经生成一个0-100的随机数，请猜测这个数是多少？")


@bot.on_command(regex=re_compile(r"(\d+)"))
def guess_number(data: Model.MESSAGE):
    this_guess = int(data.treated_msg[0])  # 获取猜测的数字（正则的第一个group）
    _session = bot.session.get(Scope.USER, "数字游戏")
    if _session is None:  # 如果session不存在，说明用户尚未输入“猜数字”开始游戏
        return
    number = _session.data["number"]  # 获取之前生成的随机数
    if this_guess == number:
        data.reply("恭喜你猜对了！")
        bot.session.end(Scope.USER, "数字游戏")
    else:
        if number < this_guess < _session.data["upper_limit"]:
            _session.data["upper_limit"] = this_guess
        elif number > this_guess > _session.data["lower_limit"]:
            _session.data["lower_limit"] = this_guess
        data.reply(
            f"猜错了，再试试吧！\n提示：{_session.data['lower_limit']}-{_session.data['upper_limit']}"
        )


@bot.on_command("开始探险")
def adventure(data: Model.MESSAGE):
    data.reply("探险开始！")
    if (_usr_session := bot.session.get(Scope.USER, "探险")) is None:
        _usr_session = bot.session.new(
            Scope.USER, "探险", data={"coin": 0}
        )  # 创建一个没有超时的session，用于保存用户金币数量
    print(_usr_session)

    # 创建BotCommandObject实例，以传入api.wait_for，等待用户输入， treat=False以在后面判断实际输入
    wait_command = BotCommandObject(command=["继续", "退出"], treat=False)
    while True:
        try:
            data = bot.api.wait_for(
                scope=Scope.USER, command_obj=wait_command, timeout=60
            )  # 等待用户输入前进或者继续，如果60秒没有收到这两个指令，则抛出WaitTimeoutError
        except WaitTimeoutError:
            data.reply("超时啦，本次探险结束")
            return
        if "退出" in data.treated_msg:
            data.reply("本次探险结束")
            return
        else:
            this_time_coin = randint(0, 100)
            _usr_session.data["coin"] += this_time_coin
            data.reply(
                f"你继续前进了一段距离，获得了{this_time_coin}个金币，现在总共有{_usr_session.data['coin']}个金币了"
            )


if __name__ == "__main__":
    bot.start()
