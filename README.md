# qg_botsdk

<div align="center">
    
<img src="https://groupprohead.gtimg.cn/13887241636967950/40?t=1650772396134" width="128"/>
    
✨用于QQ官方频道机器人，兼顾实用与容易入门的Python应用级SDK✨

![](https://img.shields.io/badge/language-python-green.svg)
![](https://img.shields.io/badge/license-MIT-orange.svg)
![](https://img.shields.io/github/v/release/GLGDLY/qg_botsdk)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/f015549b3dba4602be2fe0f5d8b0a8d5)](https://www.codacy.com/gh/GLGDLY/qg_botsdk/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=GLGDLY/qg_botsdk&amp;utm_campaign=Badge_Grade)

</div>

#### 亮点

##### -   轻量，简洁的代码结构，10行即可构建一个简单的程序

##### -   容易入门，无需学会asyncio也可使用，同时保留较高并发能力

##### - 保留官方Json结构字段，带你学习官方结构，日后可自行开发适合自己的SDK

#### 当前应用

##### - 自用（爱萌AM）

* * *

### 下载方式

-   直接下载最新release，放到项目中即可。（暂未上传pypi，无法pip install）
-   <https://github.com/GLGDLY/qg_botsdk/releases>

* * *

### 一个简单的工作流

> -   注册BOT实例，录入机器人平台获取的ID（BotAppId开发者ID）和token（机器人令牌）
> -   编写接收事件的函数[下方例子：def deliver(data)]，并借助model库检查数据格式（data: MESSAGE）
> -   绑定接收事件的函数（bind_msg、bind_dm、bind_msg_delete、bind_guild_event、bind_guild_member、bind_reaction、bind_interaction、bind_audit、bind_forum、bind_audio）
> -   开始运行机器人：bot.start()

```python
from qg_botsdk.qg_bot import BOT
from qg_botsdk.model import *


def deliver(data: MESSAGE):
    if '你好' in data.treated_msg:
        bot.send_msg('你好，世界', str(data.id), str(data.channel_id))


if __name__ == '__main__':
    bot = BOT(bot_id='xxx', bot_token='xxx', is_private=True, is_sandbox=True, max_shard=1)
    bot.bind_msg(deliver, treated_data=True)
    bot.start()
```

* * *

### 已实现事件接收（已支持解析论坛事件）

> `from qg_botsdk.model import *` 
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

> API未完善，目前仅包含自用API，SDK内调用相关API会显示详细信息，调用路径：qg_bot.Bot.{api}
> 关于API的更多详细信息可阅读官方文档介绍：<https://bot.q.qq.com/wiki/develop/api/>

-   get_bot_id：用于获取当前用户（机器人）详情
-   send_msg：发送消息
-   send_embed：发送【embed】模板消息
-   send_ark_23：发送 【23 链接+文本列表】 模板消息
-   send_ark_24：发送 【24 文本+缩略图】 模板消息
-   send_ark_37：发送 【37 大图】 模板消息
-   create_dm：用于机器人和在同一个频道内的成员创建私信会话
-   send_dm：发送私信消息
-   delete_msg：撤回频道消息（不能撤回私聊消息）
-   get_me_guilds：用于获取当前用户（机器人）所加入所有频道的列表
-   get_guild_info：用于获取 guild_id 指定的频道的详情
-   get_guild_channels：用于获取频道的所有子频道列表数据
-   get_user_info：用于获取频道中某一成员的信息数据
-   get_permission：用于发送频道API接口权限授权链接到频道
-   get_roles：用于获取频道当前的所有身份组列表
-   add_roles：为频道指定成员添加指定身份组
-   del_roles：删除频道指定成员的指定身份组

### 特殊功能

-   register_start_event：绑定一个在机器人开始运行后马上执行的函数
-   register_repeat_event：绑定一个背景重复运行的函数
-   security_check：用于使用腾讯内容检测接口进行内容检测
