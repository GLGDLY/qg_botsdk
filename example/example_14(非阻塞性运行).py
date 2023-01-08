# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 非阻塞性开始运行机器人一个实例（要求SDK版本>=2.6.0）
from asyncio import sleep

from qg_botsdk import BOT, Model

bot = BOT(bot_id="", bot_token="", is_private=True, is_sandbox=True)


@bot.bind_msg()
def deliver(data: Model.MESSAGE):
    data.reply(file_image=r"example_10_image.jpg")


if __name__ == "__main__":
    bot.start(is_blocking=False)  # 非阻塞性运行start()函数，让后续代码可以继续运行

    print("以下代码在阻塞性运行start时不会打印，而在非阻塞性时则可以运行")
    for i in range(10):
        print(f"任务{i}运行中")
        bot.loop.run_until_complete(
            sleep(1)
        )  # 注意如果有sleep相关的任务要用异步使用asyncio.sleep，而非简单time.sleep

    bot.block()  # 重新阻塞主进程，用于保持程序不会自动结束
