#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 最简单的工作流，使用logger的一个简单实例
from qg_botsdk import BOT, ApiModel, Model


def deliver(data):
    bot.logger.info("收到消息啦！")
    if "你好" in data.treated_msg:
        # 由于qq单聊和群发送消息API加入了msg_seq字段（回复消息的序号），相同的 msg_id+msg_seq 重复发送会失败
        # 因此强烈建议使用ApiModel.Message类构建消息，如需要回复多条消息便使用.update()方法，以这样的复用类来使用其内部自动递增的msg_seq
        # 也可以使用ApiModel.Message类的get_msg_seq()方法获取当前msg_seq，并在此基础上+1传入发送消息API的msg_seq参数
        msg = ApiModel.Message(content="你好，世界")
        bot.api.send_group_msg(data.group_openid, msg, message_id=data.id)
        ret = bot.api.upload_media(
            file_type=1,
            url="https://qqminiapp.cdn-go.cn/open-platform/11d80dc9/img/mini_app.2ddf1492.png",
            srv_send_msg=False,
            group_openid=data.group_openid,
        )
        msg.update(media_file_info=ret.data.file_info)
        bot.api.send_group_msg(data.group_openid, msg, message_id=data.id)
        bot.api.send_group_msg(
            data.group_openid,
            "testing",
            message_id=data.id,
            msg_seq=msg.get_msg_seq() + 1,
        )
        bot.logger.info(f"发送消息【你好，世界】到群{data.group_openid}")


if __name__ == "__main__":
    bot = BOT(
        bot_id="",
        bot_secret="",
    )
    bot.bind_group_msg(deliver)
    bot.start()
