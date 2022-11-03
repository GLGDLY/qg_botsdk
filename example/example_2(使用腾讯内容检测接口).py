# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# 使用腾讯内容检测接口的一个简单实例

from qg_botsdk import BOT, Model


def deliver(data: Model.MESSAGE):
    content = data.content
    if "内容检测" in content:
        if not bot.api.security_check(content[content.find("内容检测") + 4 :]):
            send_msg = "检测不通过，内容有违规"
        else:
            send_msg = "检测通过，内容并无违规"
        # SDK版本 >= v2.4.0 可直接使用reply()
        data.reply(send_msg)
    return


if __name__ == "__main__":
    # 注意由于安全接口封闭，仅允许小程序调用，原来的bot_secret已被废弃，转为应在security_setup()中输入小程序ID和secret
    bot = BOT(bot_id="", bot_token="", is_private=True, is_sandbox=True)
    bot.security_setup(mini_id="", mini_secret="")
    bot.bind_msg(deliver, treated_data=True)
    bot.start()
