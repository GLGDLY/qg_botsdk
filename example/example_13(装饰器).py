#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 使用装饰器与plugins的一个实例（装饰器要求SDK版本>=2.5.0 & plugins要求SDK版本>=2.5.1 & session要求SDK版本>=3.0.0）
from qg_botsdk import BOT, Model, Scope

# import example_13_plugins  # 使用plugins的方法一，直接import相应module，BOT.start()时将自动加载

bot = BOT(bot_id="", bot_token="", is_private=True, is_sandbox=True)
bot.load_plugins(
    "example_13_plugins.py"
)  # [推荐] 使用plugins的方法二，使用BOT.load_plugins()加载


# before_command代表预处理器，将在检查所有commands前执行（要求SDK版本>=2.5.2）
@bot.before_command()
def preprocessor(data: Model.MESSAGE):
    bot.logger.info(f"收到来自{data.author.username}的消息：{data.treated_msg}")


# is_short_circuit代表短路机制，即如用户输入c_0c_1，理论可触发c_0、c_1两个函数，但由于短路机制，仅会触发c_0的函数
@bot.on_command(command="c_0", is_short_circuit=False)
def c_0(data: Model.MESSAGE):
    data.reply("导入单command进行注册，用户消息包含指令c_0可触发此函数")


# is_require_at代表是否要求检测到用户@了机器人才可触发指令
@bot.on_command(command=["c_1", "case_1"], is_short_circuit=True, is_require_at=True)
def c_1(data: Model.MESSAGE):
    data.reply(
        "导入command列表进行注册，用户消息包含每个指令（c_1、case_1）均可触发此函数"
    )


# is_require_admin代表是否要求检测到用户是频道主或频道管理才可触发指令
@bot.on_command(
    regex=r"c(?:ase)?_2",
    is_short_circuit=True,
    is_require_at=True,
    is_require_admin=True,
    admin_error_msg="抱歉，你的权限不足（非频道主或管理员），不能使用此指令",
)
def c_2(data: Model.MESSAGE):
    data.reply("导入正则表达式进行注册，用户消息符合正则表达式即可触发此函数")
    bot.close()


# 注册常规bind_msg函数的装饰器使用方式
# 当连同on_command使用时，如没有触发短路，bind_msg注册的函数将在最后被调用
# 可用作类似switch case(match case)中的default(当全部指令都未触发短路时，触发最后的这一条)
@bot.bind_msg()
def deliver(data: Model.MESSAGE):
    if _session := bot.session.get(
        Scope.USER, "Plugin"
    ):  # 当前用户（Scope.USER）存在key为"Plugin"的session时
        my_session_status = _session.data[
            "status"
        ]  # 获取session的保存的数据，并从这个字典获取key为"status"的值
        bot.logger.info(f"Plugin的session状态：{my_session_status}")
        data.reply(f"Plugin的session状态：{my_session_status}")
        bot.session.end(
            Scope.USER, "Plugin"
        )  # 删除当前用户（Scope.USER）中，key为"Plugin"的session
    else:
        data.reply(file_image=r"example_10_image.jpg")


if __name__ == "__main__":
    bot.start()
