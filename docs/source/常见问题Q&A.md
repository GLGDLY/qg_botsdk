# 常见问题Q&A

## 关于机器人开发

### 1. 什么是公域和私域机器人？

-   公域代表的是可以被全局任何频道自由添加的机器人，但需要注意的是并不是说成为了公域机器人就能上频道管理添加机器人的列表，该列表为官方推荐列表，具体推荐标准可参考[此内容](https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&appChannel=share&inviteCode=1W4XSR8&appChannel=share&contentID=QPDs&businessType=2&from=181174&shareSource=5&biz=ka)

-   私域代表的是机器人可以调用更多的API、受到的限制会更少，但机器人仅能被添加到自己是频道主或管理员的频道

-   更多详情可参考[官方说明](https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&appChannel=share&inviteCode=1W4XSHL&appChannel=share&contentID=SmcF&businessType=2&from=181174&shareSource=5&biz=ka)

### 2. 什么是沙箱环境？

-   沙箱环境就是一个封闭性的环境，在不影响应用环境的主体程序运行的同时，允许同时开启沙箱环境下的机器人程序，仅接收沙箱频道消息并进行相关的一些测试。

-   开启沙箱环境可以在实例化`BOT()`时，添加参数`is_sandbox=True`，如：

```python
from qg_botsdk.qg_bot import BOT

bot = BOT('BotAppID', 'BotToken', is_sandbox=True)
```

### 3. 为什么我仅能接收艾特消息？

-   SDK会根据机器人主体为公域机器人或私域机器人，自动判断接收艾特或全部消息——公域机器人仅能接收艾特消息，私域机器人可接收全部消息。

-   系统将默认机器人为公域机器人（`is_private=False`），如需更改为私域机器人模式，可在实例化`BOT()`时，添加参数`is_private=True`，如：

```python
from qg_botsdk.qg_bot import BOT

bot = BOT('BotAppID', 'BotToken', is_private=True)
```

### 4. 接收消息或其他事件时，函数名应该是什么？

-   SDK并没有限制接收消息的函数名称，大家完全可以自由发挥。

-   那么系统如何知道这是接收什么事件的函数呢？关键在于bind_msg等bind开头的绑定方法上，只要大家把函数通过一系列bind方法进行绑定，系统就能知道要给你这个函数推送相应的事件了。

-   具体例子如下：

```python
from qg_botsdk.qg_bot import BOT


# 创建接收消息事件的函数，其中带有一个参数位去接收数据；
# 函数目前的名称为deliver，但大家完全可以改为on_msg_function等其他名字；
# 只需在下方bot.bind_msg()中同时更改即可，如bot.bind_msg(on_msg_function)；
# 同理，其参数data也不需要一定是data，也可以是msg等；
# 只需要在调用其中数据时同时更改就行，如msg.treated_msg、msg.channel_id等
def deliver(data):
    if '你好' in data.treated_msg:
        bot.send_msg(data.channel_id, '你好，世界', message_id=data.id)


bot = BOT(bot_id='BotAppID', bot_token='BotToken')
bot.bind_msg(deliver)  # 绑定接收消息事件的函数
bot.start()
```

### 4. 为什么官方文档有Intents的东西，但SDK没有呢？

-   因为SDK已经简化了整个调用的流程，无需大家重复调用。SDK把对intents位的比对内嵌到了bind系列的方法中（如bind_msg），只需要大家注册相应的函数，系统就会自动比对intents位移、注册相关事件接收、并在收到事件后向相关函数推送事件。因此，大家无需去学习intents的方法，只需要实例化机器人调用、注册事件函数、开启机器人即可简洁地使用机器人。

> 更多常见问题可参考：<https://qqbotdoc.rhodescafe.net/wiki/faq.html#%E9%80%9A%E7%94%A8>
