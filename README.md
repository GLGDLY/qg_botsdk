<div align="center">
    
![qg_botsdk](https://socialify.git.ci/GLGDLY/qg_botsdk/image?description=1&font=Source%20Code%20Pro&forks=1&issues=1&language=1&logo=https%3A%2F%2Fgithub.com%2Ftencent-connect%2Fbot-docs%2Fblob%2Fmain%2Fdocs%2F.vuepress%2Fpublic%2Ffavicon-64px.png%3Fraw%3Dtrue&name=1&owner=1&pattern=Floating%20Cogs&pulls=1&stargazers=1&theme=Light)

[![Language](https://img.shields.io/badge/language-python-green.svg?style=plastic)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg?style=plastic)](https://github.com/GLGDLY/qg_botsdk/blob/master/LICENSE)
[![Pypi](https://img.shields.io/pypi/dw/qg-botsdk?style=plastic&color=blue)](https://pypi.org/project/qg-botsdk/)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/f015549b3dba4602be2fe0f5d8b0a8d5)](https://app.codacy.com/gh/GLGDLY/qg_botsdk/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![docs](https://readthedocs.org/projects/qg-botsdk/badge/?version=latest)](https://qg-botsdk.readthedocs.io/zh_CN/latest/)

✨ 用于 QQ 官方频道机器人，兼顾实用与容易入门的 Python 应用级 SDK✨

[文档](https://qg-botsdk.readthedocs.io/zh_CN/latest/)
·
[例程](https://github.com/GLGDLY/qg_botsdk/tree/master/example)
·
[快速入门](https://qg-botsdk.readthedocs.io/zh_CN/latest/quick_start)

</div>

#### 引言

对于使用 python 进行频道官方机器人开发而言，市面上确实有不同的 sdk 可以选用，但其很多只提供异步 asyncio+类继承的开发方式，对于不会相关技巧的朋友们，尤其新手，会有开发难度。

为此，qg_botsdk 相应提供了另一个选择，这一款 sdk 虽然同样使用 asyncio 编写 sdk 底层，但其同时提供了 threading 和 asyncio 封装下的应用层调用，以抽象化封装的库编写方式，极大地降低应用层的开发难度。

#### 亮点

##### - 已支持 Websocket、Webhook、Remote Webhook（wh 转 ws 允许本地调试）三种连接方式

##### - 已支持 SDK 层面的沙箱处理，允许沙箱过滤外部消息、外部过滤沙箱消息；已支持频道、频道私信、群、QQ 私信四种沙箱过滤模式

##### - 两种应用层开发方式（threading、asyncio），可根据自己的喜好选择，而底层均为 asyncio 实现，保持高并发能力

##### - 灵活的构建方式，即使官方删除或新增字段，SDK 也不会规范于原来的数据格式，而会把真实数据反馈给你

##### - 轻量，简洁，统一的代码结构，通过录入回调函数处理不同事件，10 行即可构建一个简单的程序

##### - 容易入门，无需学会 asyncio、类继承等编程技巧也可使用，同时保留较高并发能力

##### - 保留官方 http API 中 Json 数据的结构字段，带你学习官方结构，日后可自行开发适合自己的 SDK

##### - 简单易用的 plugins 编写与加载，使用例子可参阅 [example_13(装饰器).py](<./example/example_13(%E8%A3%85%E9%A5%B0%E5%99%A8).py>)

##### - 方便多场景（频道+群等）构建机器人的抽象化封装，使用例子可参阅 [example_16(Q 群简单工作流).py](<./example/example_16(Q%E7%BE%A4%E7%AE%80%E5%8D%95%E5%B7%A5%E4%BD%9C%E6%B5%81).py>)

---

### 下载方式

- pip 安装（推荐）：

```shell bash
pip install qg-botsdk   # 注意是qg-botsdk（中线），不是qg_botsdk（底线）
```

---

### 一个简单的工作流

> - 注册 BOT 实例，录入机器人平台获取的 ID（BotAppId 开发者 ID）和 token（机器人令牌）
> - 编写接收事件的函数->下方例子：`def deliver(data)`，并可借助 model 库检查数据格式（`data: Model.MESSAGE`）
> - 绑定接收事件的函数（bind_msg、bind_dm、bind_msg_delete、bind_guild_event、bind_guild_member、bind_reaction、bind_interaction、bind_audit、bind_forum、bind_audio）
> - 开始运行机器人：bot.start()

```python
from qg_botsdk import BOT, Model   # 导入SDK核心类（BOT）、所有数据模型（Model）

bot = BOT(bot_id='xxx', bot_token='xxx', is_private=True, is_sandbox=True)   # 实例化SDK核心类


@bot.bind_msg()   # 绑定接收消息事件的函数
def deliver(data: Model.MESSAGE):   # 创建接收消息事件的函数
    if '你好' in data.treated_msg:   # 判断消息是否存在特定内容
        data.reply('你好，世界')   # 发送被动回复（带message_id直接reply回复）
        # 如需使用如 Embed 等消息模板，可传入相应结构体， 如：
        # data.reply(ApiModel.MessageEmbed(title="你好", content="世界"))


if __name__ == '__main__':
    bot.start()   # 开始运行机器人
```

---

### 指令装饰器

SDK 同时已经在内部实现指令装饰器：

```python
from qg_botsdk import BOT, Model

bot = BOT(bot_id='xxx', bot_token='xxx', is_private=True, is_sandbox=True)

# before_command代表预处理器，将在检查所有commands前执行（要求SDK版本>=2.5.2）
@bot.before_command()
def preprocessor(data: Model.MESSAGE):
    bot.logger.info(f"收到来自{data.author.username}的消息：{data.treated_msg}")


@bot.on_command(
    regex=r"你好(?:机器人)?",  # 正则表达式，匹配用户消息
    is_short_circuit=True,    # is_short_circuit代表短路机制，根据注册顺序，匹配到即停止匹配，但不影响bind_msg()
    is_require_at=True,       # is_require_at代表是否要求检测到用户@了机器人才可触发指令
    is_require_admin=True,    # is_require_admin代表是否要求检测到用户是频道主或频道管理才可触发指令
    admin_error_msg="抱歉，你的权限不足（非频道主或管理员），不能使用此指令",
)
def command(data: Model.MESSAGE):
    data.reply("你好，世界")


if __name__ == '__main__':
    bot.start()
```

---

### 相关链接

- 更多完整例程：

  - [example](https://github.com/GLGDLY/qg_botsdk/tree/master/example)

- 文档：

  - [readthedocs](https://qg-botsdk.readthedocs.io/zh_CN/latest/)

- 官方注册机器人：<https://q.qq.com/#/>

- 官方 API 文档：<https://bot.q.qq.com/wiki/develop/api/>

- SDK QQ 交流群：<https://jq.qq.com/?_wv=1027&k=3NnWvGpz>
