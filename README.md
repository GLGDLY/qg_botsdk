# qg_botsdk

<div align="center">
    
<img src="https://groupprohead.gtimg.cn/13887241636967950/40?t=1650772396134" width="128"/>
    
✨用于QQ官方频道机器人，兼顾实用与容易入门的Python应用级SDK✨

![](https://img.shields.io/badge/language-python-green.svg)
![](https://img.shields.io/badge/license-MIT-orange.svg)
![](https://img.shields.io/github/v/release/GLGDLY/qg_botsdk)
</div>

#### 亮点
###### - 轻量，简洁的代码结构，10行即可构建一个简单的程序
###### - 容易入门，无需学会asyncio也可使用，同时保留较高并发能力
###### - 保留官方json格式，带你学习官方结构，日后可自行开发适合自己的sdk

#### 当前应用
###### - 自用（爱萌AM）

------------
### 下载方式

- 直接下载最新release，放到项目中即可。（暂未上传pypi，无法pip install）
- https://github.com/GLGDLY/qg_botsdk/releases

------------
### 一个简单的工作流

> - 注册BOT实例，录入机器人平台获取的ID（BotAppId开发者ID）和token（机器人令牌）
> - 绑定接收事件的函数（bind_msg、bind_dm、bind_msg_delete、bind_guild_event、bind_guild_member、bind_reaction、bind_interaction、bind_audit、bind_forum、bind_audio）
> - 开始运行机器人：bot.start()

```python
from qg_bot import BOT


def deliver(json_data):
    if '你好' in json_data['treated_msg']:
        bot.send_msg('你好，世界', str(json_data['d']['id']), str(json_data['d']['channel_id']))


if __name__ == '__main__':
    bot = BOT(bot_id='xxx', bot_token='xxx', is_private=True, is_sandbox=True, max_shard=1)
    bot.bind_msg(deliver, treated_data=True)
    bot.start()
```

------------
### 已实现事件接收

- bind_msg
- bind_dm
- bind_msg_delete
- bind_guild_event
- bind_guild_member
- bind_reaction
- bind_interaction
- bind_audit
- bind_forum
- bind_audio

### 已实现API

> API未完善，目前仅包含自用API，sdk内调用相关API会显示详细信息，调用路径：qg_bot.Bot.{api}

- get_bot_id
- send_msg
- send_embed
- send_ark_23
- create_dm
- send_dm
- delete_msg
- get_me_guilds
- get_guild_info
- get_guild_channels
- get_user_info
- get_permission
- get_roles
- add_roles
- del_roles

### 特殊功能

- register_start_event
- register_repeat_event
- security_check
