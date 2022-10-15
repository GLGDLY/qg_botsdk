.. image:: https://socialify.git.ci/GLGDLY/qg_botsdk/image?description=1&font=Source%20Code%20Pro&forks=1&issues=1&language=1&logo=https%3A%2F%2Fgithub.com%2Ftencent-connect%2Fbot-docs%2Fblob%2Fmain%2Fdocs%2F.vuepress%2Fpublic%2Ffavicon-64px.png%3Fraw%3Dtrue&name=1&owner=1&pattern=Floating%20Cogs&pulls=1&stargazers=1&theme=Light

|

.. image:: https://img.shields.io/badge/language-python-green.svg?style=plastic
   :target: https://www.python.org/
.. image:: https://img.shields.io/badge/license-MIT-orange.svg?style=plastic
   :target: https://github.com/GLGDLY/qg_botsdk/blob/master/LICENSE
.. image:: https://img.shields.io/github/v/release/GLGDLY/qg_botsdk?style=plastic
   :target: https://github.com/GLGDLY/qg_botsdk/releases
.. image:: https://img.shields.io/pypi/dw/qg-botsdk?style=plastic&color=blue
   :target: https://pypi.org/project/qg-botsdk/
.. image:: https://app.codacy.com/project/badge/Grade/f015549b3dba4602be2fe0f5d8b0a8d5
   :target: https://www.codacy.com/gh/GLGDLY/qg_botsdk/dashboard?utm_source=github.com&utm_medium=referral&utm_content=GLGDLY/qg_botsdk&utm_campaign=Badge_Grade
.. image:: https://readthedocs.org/projects/qg-botsdk/badge/?version=latest
   :target: https://qg-botsdk.readthedocs.io/zh_CN/latest/

亮点
=====

-   灵活的构建方式，即使官方删除或新增字段，SDK也不会规范于原来的数据格式，而会把真实数据反馈给你

-   轻量，简洁，统一的代码结构，10行即可构建一个简单的程序

-   容易入门，无需学会asyncio也可使用，同时保留较高并发能力

-   保留官方http API中Json数据的结构字段，带你学习官方结构，日后可自行开发适合自己的SDK

-   迅速的更新速度，跟上最新潮流（v2.3.6已更新发送markdown消息能力，使用例子可参阅 `example_12(markdown).py <./example/example_12(markdown).py>`_

-   简单易用的plugins编写与加载，使用例子可参阅 `example_13(装饰器).py <./example/example_13(%E8%A3%85%E9%A5%B0%E5%99%A8).py>`_

下载方式
==========

-   直接下载 `最新release <https://github.com/GLGDLY/qg_botsdk/releases>`_ ，放到项目中即可
-   pip安装（推荐）：

.. code-block:: bash

    pip install qg-botsdk

**注意是qg-botsdk（中线），不是qg_botsdk（底线）**

一个简单的工作流
==================

| -   注册BOT实例，录入机器人平台获取的ID（BotAppId开发者ID）和token（机器人令牌）
| -   编写接收事件的函数->下方例子：``def deliver(data)``，并可借助model库检查数据格式（``data: Model.MESSAGE``）
| -   绑定接收事件的函数（bind_msg、bind_dm、bind_msg_delete、bind_guild_event、bind_guild_member、bind_reaction、bind_interaction、bind_audit、bind_forum、bind_audio）
| -   开始运行机器人：bot.start()

.. code-block:: python

    from qg_botsdk import BOT, Model   # 导入SDK核心类（BOT）、所有数据模型（Model）

    bot = BOT(bot_id='xxx', bot_token='xxx', is_private=True, is_sandbox=True)   # 实例化SDK核心类


    @bot.bind_msg()   # 绑定接收消息事件的函数
    def deliver(data: Model.MESSAGE):   # 创建接收消息事件的函数
        if '你好' in data.treated_msg:   # 判断消息是否存在特定内容
            data.reply('你好，世界')   # 发送被动回复（带message_id直接reply回复）


    if __name__ == '__main__':
        bot.start()   # 开始运行机器人

已实现事件接收（已支持解析论坛事件）
===========================================

::

    from qg_botsdk.model import Model
    此库为所有事件的数据格式结构，可套用到代码以检查结构是否正确

-   bind_msg
-   bind_dm
-   bind_msg_delete
-   bind_guild_event
-   bind_guild_member
-   bind_reaction
-   bind_interaction
-   bind_audit
-   bind_forum
-   bind_audio

已实现API
=========

::

    - API已基本完善，具体详情可查阅：https://qg-botsdk.readthedocs.io/zh_CN/latest/API.html
    - 关于API的更多详细信息可阅读官方文档介绍：https://bot.q.qq.com/wiki/develop/api/

-   get_bot_id
-   get_bot_info
-   get_bot_guilds
-   get_guild_info
-   get_guild_channels
-   get_channels_info
-   create_channels
-   patch_channels
-   delete_channels
-   get_guild_members
-   get_role_members
-   get_member_info
-   delete_member
-   get_guild_roles
-   create_role
-   patch_role
-   delete_role
-   create_role_member
-   delete_role_member
-   get_channel_member_permission
-   put_channel_member_permission
-   get_channel_role_permission
-   put_channel_role_permission
-   get_message_info
-   send_msg
-   send_embed
-   send_ark_23
-   send_ark_24
-   send_ark_37
-   send_markdown
-   delete_msg
-   get_guild_setting
-   create_dm_guild
-   send_dm
-   delete_dm_msg
-   mute_all_member
-   mute_member
-   mute_members
-   create_announce
-   delete_announce
-   create_pinmsg
-   delete_pinmsg
-   get_pinmsg
-   get_schedules
-   get_schedule_info
-   create_schedule
-   patch_schedule
-   delete_schedule
-   create_reaction
-   delete_reaction
-   get_reaction_users
-   control_audio
-   bot_on_mic
-   bot_off_mic
-   get_threads
-   get_thread_info
-   create_thread
-   delete_thread
-   get_guild_permissions
-   create_permission_demand

特殊功能
========

-   register_start_event：绑定一个在机器人开始运行后马上执行的函数
-   register_repeat_event：绑定一个背景重复运行的函数
-   security_check：用于使用腾讯内容检测接口进行内容检测


相关链接
========

-   文档：
     * `readthedocs <https://qg-botsdk.readthedocs.io/zh_CN/latest/>`_
     * `thoughts <https://thoughts.teambition.com/sharespace/6289c429eb27e90041a58b57/docs/6289c429eb27e90041a58b51>`_
-   官方注册机器人：https://q.qq.com/#/
-   官方API文档：https://bot.q.qq.com/wiki/develop/api/
-   SDK QQ交流群：https://jq.qq.com/?_wv=1027&k=3NnWvGpz