# qg_botsdk

<div align="center">
    
<img src="https://groupprohead.gtimg.cn/13887241636967950/40?t=1650772396134" width="128"/>

✨用于QQ官方频道机器人，兼顾实用与容易入门的Python应用级SDK✨

[![Language](https://img.shields.io/badge/language-python-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](https://github.com/GLGDLY/qg_botsdk/blob/master/LICENSE)
[![Releases](https://img.shields.io/github/v/release/GLGDLY/qg_botsdk)](https://github.com/GLGDLY/qg_botsdk/releases)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/f015549b3dba4602be2fe0f5d8b0a8d5)](https://www.codacy.com/gh/GLGDLY/qg_botsdk/dashboard?utm_source=github.com&utm_medium=referral&utm_content=GLGDLY/qg_botsdk&utm_campaign=Badge_Grade)

[文档](https://thoughts.teambition.com/sharespace/6289c429eb27e90041a58b57/docs/6289c429eb27e90041a58b51)
·
[下载](https://github.com/GLGDLY/qg_botsdk/releases)
·
[快速入门](https://thoughts.teambition.com/sharespace/6289c429eb27e90041a58b57/docs/6289c429eb27e90041a58b52)

</div>

#### 亮点

##### -   轻量，简洁的代码结构，10行即可构建一个简单的程序

##### -   容易入门，无需学会asyncio也可使用，同时保留较高并发能力

##### - 保留官方Json结构字段，带你学习官方结构，日后可自行开发适合自己的SDK

#### 当前应用

##### - 自用（爱萌AM）：<https://qun.qq.com/qunpro/robot/share?robot_appid=101986932>

* * *

### 下载方式

-   直接下载最新release，放到项目中即可：<https://github.com/GLGDLY/qg_botsdk/releases>
-   pip安装：
    > -   Windows: `py -m pip install qg-botsdk`
    > -   Linux: `python3 -m pip install qg-botsdk`

* * *

### 一个简单的工作流

> -   注册BOT实例，录入机器人平台获取的ID（BotAppId开发者ID）和token（机器人令牌）
> -   编写接收事件的函数[下方例子：def deliver(data)]，并借助model库检查数据格式（data: MESSAGE）
> -   绑定接收事件的函数（bind_msg、bind_dm、bind_msg_delete、bind_guild_event、bind_guild_member、bind_reaction、bind_interaction、bind_audit、bind_forum、bind_audio）
> -   开始运行机器人：bot.start()

```python
from qg_botsdk.qg_bot import BOT   # 导入SDK核心类
from qg_botsdk.model import Model   # 导入所有数据模型


def deliver(data: Model.MESSAGE):   # 创建接收消息事件的函数
    if '你好' in data.treated_msg:
        bot.send_msg(data.channel_id, '你好，世界', message_id=data.id)


if __name__ == '__main__':
    bot = BOT(bot_id='xxx', bot_token='xxx', is_private=True, is_sandbox=True)   # 实例化SDK核心类
    bot.bind_msg(deliver, treated_data=True)   # 绑定接收消息事件的函数
    bot.start()   # 开始运行机器人
```

* * *

### 已实现事件接收（已支持解析论坛事件）

> `from qg_botsdk.model import Model` 
>
> 此库为所有事件的数据格式结构，可套用到代码以检查结构是否正确

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

### 已实现API

> API已基本完善，具体详情可查阅：<https://thoughts.teambition.com/sharespace/6289c429eb27e90041a58b57/docs/6289c429eb27e90041a58b54>

> 关于API的更多详细信息可阅读官方文档介绍：<https://bot.q.qq.com/wiki/develop/api/>

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

### 特殊功能

-   register_start_event：绑定一个在机器人开始运行后马上执行的函数
-   register_repeat_event：绑定一个背景重复运行的函数
-   security_check：用于使用腾讯内容检测接口进行内容检测

### 相关链接：

-   文档：<https://thoughts.teambition.com/sharespace/6289c429eb27e90041a58b57/docs/6289c429eb27e90041a58b51>
-   官方注册机器人：<https://q.qq.com/#/>
-   官方API文档：<https://bot.q.qq.com/wiki/develop/api/>
-   支持我的创作：<https://afdian.net/@GLGDLY>
