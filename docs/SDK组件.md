# SDK组件

本内容将介绍SDK核心类内提供的组件内容。

## 引言-SDK组件

让我们先重温一下简单的工作流：

```python
from qg_botsdk import BOT

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_msg(deliver)
bot.start()
```

在这个工作流中，我们可以看到SDK的核心类就是qg_botsdk.qg_bot.BOT，因此SDK的组件均是在这个核心类之下的应用，而核心类会分为三个部分：主要组件、绑定组件、辅助组件、API组件。

## 主要组件

### 实例化机器人

-   以实例化注册机器人，支持同程序用多个进程注册多个机器人

```python
BOT(bot_id='xxx', bot_token='xxx')
# 路径：qg_botsdk.qg_bot.BOT()
```

| 参数                    |        |        |                                                    |
| --------------------- | ------ | ------ | -------------------------------------------------- |
| 字段名                   | 类型     | 默认值    | 说明                                                 |
| bot_id                | string | 无，必选参数 | 机器人平台BotAppID                                      |
| bot_token             | string | 无，必选参数 | 机器人平台机器人令牌                                         |
| bot_secret            | string | None   | 机器人平台机器人密钥                                         |
| is_private            | bool   | False  | 是否私域机器人，默认为公域（只订阅艾特消息，不订阅全部）                       |
| is_sandbox            | bool   | False  | 是否开启沙箱环境测试                                         |
| max_shard             | int    | 5      | 最大分片数限制（SDK版本2.3.1后已遗弃，转为自定义shard_no以及total_shard） |
| no_permission_warning | bool   | True   | 否开启当机器人获取疑似权限不足的事件时的警告提示，默认开启                      |
| is_async              | bool   | False  | 使用同步api还是异步api，默认False（使用同步）                       |
| is_retry              | bool   | True   | 使用api时，如遇可重试的错误码是否自动进行重试（需求SDK版本>=2.2.8）           |
| is_log_error          | bool   | True   | 使用api时，如返回的结果为不成功，可自动log输出报错信息（需求SDK版本>=2.2.10）    |
| shard_no              | int    | 0      | 当前分片数，如不熟悉相关配置请不要轻易改动此项（需求SDK版本>=2.3.1）            |
| total_shard           | int    | 1      | 最大分片数，如不熟悉相关配置请不要轻易改动此项（需求SDK版本>=2.3.1）            |
| max_workers           | int    | None   | 在同步模式下，允许同时运行的最大线程数（需求SDK版本>=2.3.5）                |

### 开始机器人

-   开始运行实例化后的机器人

```python
bot.start()
# 路径：qg_botsdk.qg_bot.BOT().start()
```

> 无参数

### 结束机器人

-   结束运行中的机器人

```python
bot.close()
# 路径：qg_botsdk.qg_bot.BOT().close()
```

> 无参数

### 获取机器人信息（需求SDK版本>=2.3.2）

-   获取id（机器人的频道用户id）、username、avatar等机器人的频道资料

```yaml
bot.robot:
  - bot.robot.id
  - bot.username
  - bot.avatar
# 路径：qg_botsdk.qg_bot.BOT().robot.id/username/avatar
```

> 无参数

### 获取SDK内置锁（需求SDK版本>=2.4.3）

-   返回SDK内置锁（根据SDK并发配置分配thread或async的Lock）

```yaml
bot.lock
# 路径：qg_botsdk.qg_bot.BOT().robot.lock
```

> 无参数

### 指令装饰器（需求SDK版本>=2.5.0）

-   指令装饰器。用于快速注册消息事件

```python
@bot.on_command(command='c_0')
def c_0(data: Model.MESSAGE):
    data.reply('消息包含c_0可触发此函数')
# 路径：qg_botsdk.qg_bot.BOT().on_command
```

| 参数                    |        |        |                                                    |
| --------------------- | ------ | ------ | -------------------------------------------------- |
| 字段名                   | 类型     | 默认值    | 说明                                                 |
| command           | List[str], str | None | 可触发事件的指令列表，与正则regex互斥，优先使用此项                   |
| regex             | Pattern, str   | None | 可触发指令的正则compile实例或正则表达式，与指令表互斥                 |
| is_require_at     | bool           | False| 是否要求必须艾特机器人才能触发指令                                   |
| is_short_circuit  | bool           | False| 如果触发指令成功是否短路不运行后续指令（将根据注册顺序和command先regex后排序指令的短路机制）   |
| is_require_admin  | bool           | False| 是否要求频道主或或管理才可触发指令                                   |

> （更多相关例子可参阅<https://github.com/GLGDLY/qg_botsdk/blob/master/example/example_13(%E8%A3%85%E9%A5%B0%E5%99%A8).py>）

## 绑定组件（SDK版本>=2.5.0支持装饰器）

> 装饰器用法：

```python
bot = BOT(bot_id='xxx', bot_token='xxx')

@bot.bind_msg()
def msg_function(data):   # 可使用 def msg_function(data: Model.MESSAGE): 调用模型数据
	"""
	这是接收消息的函数，包含了一个data的参数以接收Object类型数据；
	处理后的消息数据treated_msg为：data.treated_msg
	处理前的消息数据为：data.content
	:param data: 可从model取用模型数据，方法 —— data: Model.MESSAGE
	"""
	print('收到了消息： %s ！' % data.treated_msg)
```

### 绑定接收消息事件

-   用作绑定接收消息的函数，将根据机器人是否公域自动判断接收艾特或所有消息

-   接收`AT_MESSAGE_CREATE` `MESSAGE_CREATE`

```python
def msg_function(data):   # 可使用 def msg_function(data: Model.MESSAGE): 调用模型数据
	"""
	这是接收消息的函数，包含了一个data的参数以接收Object类型数据；
	处理后的消息数据treated_msg为：data.treated_msg
	处理前的消息数据为：data.content
	:param data: 可从model取用模型数据，方法 —— data: Model.MESSAGE
	"""
	print('收到了消息： %s ！' % data.treated_msg)


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_msg(on_msg_function=msg_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_msg()
```

| 参数              |            |        |                                                |
| --------------- | ---------- | ------ | ---------------------------------------------- |
| 字段名             | 类型         | 默认值    | 说明                                             |
| on_msg_function | function函数 | 无，必选参数 | 该函数应包含一个参数以接收Object消息数据进行处理                    |
| treated_data    | bool       | True   | 是否返回经转义处理的文本，如是则会在返回的Object中添加一个treated_msg的子类 |

> -   公域机器人只能收到@机器人的消息（AT_MESSAGE_CREATE）；私域机器人能收到频道内所有消息（MESSAGE_CREATE）

> -   此绑定组件通过注册机器人时is_private判断公域私域，再自动判断订阅哪一种消息类型。

> -   treated_msg会自动去除开头@机器人的字段、/ 的字段等，如不想使用此功能，可直接使用 `data.content` 获取未经处理的数据

### 绑定接收私信消息事件

-   用作绑定接收私信消息的函数

-   接收`DIRECT_MESSAGE_CREATE`

```python
def dm_function(data):   # 可使用 def msg_function(data: Model.DIRECT_MESSAGE): 调用模型数据
	"""
	这是接收私信的函数，包含了一个data的参数以接收Object类型数据
	:param data: 可从model取用模型数据，方法 —— data: Model.DIRECT_MESSAGE
	"""
	print('收到了消息： %s ！' % data.treated_msg)


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_dm(on_dm_function=dm_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_dm()
```

| 参数             |            |        |                                                |
| -------------- | ---------- | ------ | ---------------------------------------------- |
| 字段名            | 类型         | 默认值    | 说明                                             |
| on_dm_function | function函数 | 无，必选参数 | 该函数应包含一个参数以接收Object消息数据进行处理                    |
| treated_data   | bool       | True   | 是否返回经转义处理的文本，如是则会在返回的Object中添加一个treated_msg的子类 |

> -   treated_msg会自动去除开头@机器人的字段、/ 的字段等，如不想使用此功能，可直接使用 `data.content` 获取未经处理的数据

### 绑定撤回消息事件

-   用作绑定接收消息撤回事件的函数，注册时将自动根据公域私域注册艾特或全部消息，但不会主动注册私信事件

-   接收`MESSAGE_DELETE` `PUBLIC_MESSAGE_DELETE` `DIRECT_MESSAGE_DELETE`

```python
def delete_function(data):   # 可使用 def msg_function(data: Model.MESSAGE_DELETE): 调用模型数据
	"""
	这是接收撤回事件的函数，包含了一个data的参数以接收Object类型数据
	:param data: 可从model取用模型数据，方法 —— data: Model.MESSAGE_DELETE
	"""
	print('ID：%s 的用户撤回了用户 %s(ID：%s)的消息【%s】' % (
        data.op_user.id, data.message.author.username, data.message.author.id, data.message.channel_id))


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_msg_delete(on_delete_function=delete_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_msg_delete()
```

| 参数                 |            |        |                                                |
| ------------------ | ---------- | ------ | ---------------------------------------------- |
| 字段名                | 类型         | 默认值    | 说明                                             |
| on_delete_function | function函数 | 无，必选参数 | 该函数应包含一个参数以接收Object消息数据进行处理                    |
| treated_data       | bool       | True   | 是否返回经转义处理的文本，如是则会在返回的Object中添加一个treated_msg的子类 |

> 如绑定了私信事件，撤回消息事件则将包含私信的撤回消息（DIRECT_MESSAGE_DELETE）

### 绑定频道事件

-   用作绑定接收频道信息的函数

-   接收`GUILD_CREATE` `GUILD_UPDATE` `GUILD_DELETE` 【`CHANNEL_CREATE` `CHANNEL_UPDATE` `CHANNEL_DELETE`】-> \*\*\*注意SDK版本v2.2.4后，此项不再接收channel事件，改为下方【绑定子频道事件】进行接收

```python
def guild_function(data):   # 可使用 def msg_function(data: GUILDS): 调用模型数据
	"""
	这是接收频道事件的函数，包含了一个data的参数以接收Object类型数据
	:param data: 可从model取用模型数据，方法 —— data: Model.GUILDS
	"""
	print('收到了来自频道 %s（ID:%s） 的数据更新：%s' % (
data.name, data.id, data.t))  # data.t代表接收的事件名，如GUILD_CREATE


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_guild_event(on_guild_event_function=guild_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_guild_event()
```

| 参数                      |            |        |                             |
| ----------------------- | ---------- | ------ | --------------------------- |
| 字段名                     | 类型         | 默认值    | 说明                          |
| on_guild_event_function | function函数 | 无，必选参数 | 该函数应包含一个参数以接收Object消息数据进行处理 |

### 绑定子频道事件（需求sdk版本≥v2.2.4）

-   用作绑定接收子频道信息的函数

-   接收`CHANNEL_CREATE` `CHANNEL_UPDATE` `CHANNEL_DELETE`

```python
def channel_function(data):   # 可使用 def msg_function(data: Model.CHANNELS): 调用模型数据
	"""
	这是接收频道事件的函数，包含了一个data的参数以接收Object类型数据
	:param data: 可从model取用模型数据，方法 —— data: Model.CHANNELS
	"""
	print('收到了来自子频道 %s（ID:%s） 的数据更新：%s' % (
data.name, data.id, data.t))  # data.t代表接收的事件名，如CHANNEL_CREATE 


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_channel_event(on_channel_event_function=channel_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_channel_event()
```

| 参数                        |            |        |                             |
| ------------------------- | ---------- | ------ | --------------------------- |
| 字段名                       | 类型         | 默认值    | 说明                          |
| on_channel_event_function | function函数 | 无，必选参数 | 该函数应包含一个参数以接收Object消息数据进行处理 |

### 绑定频道成员

-   用作绑定接收频道信息的函数

-   接收`GUILD_MEMBER_ADD` `GUILD_MEMBER_UPDATE` `GUILD_MEMBER_REMOVE`

```python
def guild_member_function(data):   # 可使用 def msg_function(data: Model.GUILD_MEMBERS): 调用模型数据
	"""
	这是接收频道成员事件的函数，包含了一个data的参数以接收Object类型数据
	:param data: 可从model取用模型数据，方法 —— data: Model.GUILD_MEMBERS
	"""
	print('收到了来自频道ID:%s 的成员 %s 的数据更新：%s' % (
data.id, data.user.username, data.t))


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_guild_event(on_guild_member_function=guild_member_function)
# 路径：qg_botsdk.qg_bot.BOT().on_guild_member_function()
```

| 参数                       |            |        |                             |
| ------------------------ | ---------- | ------ | --------------------------- |
| 字段名                      | 类型         | 默认值    | 说明                          |
| on_guild_member_function | function函数 | 无，必选参数 | 该函数应包含一个参数以接收Object消息数据进行处理 |

### 绑定表情表态事件

-   用作绑定接收表情表态信息的函数

-   接收`MESSAGE_REACTION_ADD` `MESSAGE_REACTION_REMOVE`

```python
def reaction_function(data):   # 可使用 def msg_function(data: Model.REACTION): 调用模型数据
	"""
	这是接收表情表态事件的函数，包含了一个data的参数以接收Object类型数据
	:param data: 可从model取用模型数据，方法 —— data: Model.REACTION
	"""
	if data.t == 'MESSAGE_REACTION_ADD':
		bot.api.send_msg('%s 在频道 %s 子频道 %s 新增了新的表情动态！' % (data.user_id, data.guild_id, data.channel_id))


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_reaction(on_reaction_function=reaction_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_reaction()
```

| 参数                   |            |        |                             |
| -------------------- | ---------- | ------ | --------------------------- |
| 字段名                  | 类型         | 默认值    | 说明                          |
| on_reaction_function | function函数 | 无，必选参数 | 该函数应包含一个参数以接收Object消息数据进行处理 |

### 绑定互动事件

-   用作绑定接收互动事件的函数，当前未有录入数据结构

-   接收`INTERACTION_CREATE`

```python
def interaction_function(data):
	"""
	这是接收互动事件的函数，包含了一个data的参数以接收Object类型数据
	:param data: 当前未有录入数据结构
	"""
	print('暂时未有数据结构记录')


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_interaction(on_interaction_function=interaction_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_interaction()
```

| 参数                      |            |        |                             |
| ----------------------- | ---------- | ------ | --------------------------- |
| 字段名                     | 类型         | 默认值    | 说明                          |
| on_interaction_function | function函数 | 无，必选参数 | 该函数应包含一个参数以接收Object消息数据进行处理 |

### 绑定审核事件

-   用作绑定接收审核事件的函数

-   接收`MESSAGE_AUDIT_PASS` `MESSAGE_AUDIT_REJECT`

```python
def audit_function(data):   # 可使用 def msg_function(data: Model.MESSAGE_AUDIT): 调用模型数据
	"""
	这是接收审核事件的函数，包含了一个data的参数以接收Object类型数据
	:param data: 可从model取用模型数据，方法 —— data: Model.MESSAGE_AUDIT
	"""
	if data.t == 'MESSAGE_AUDIT_PASS':
		bot.logger.info('主动消息审核通过啦，已自动发往子频道%s了！' % data.channel_id)


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_audit(on_audit_function=audit_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_audit()
```

| 参数                |            |        |                             |
| ----------------- | ---------- | ------ | --------------------------- |
| 字段名               | 类型         | 默认值    | 说明                          |
| on_audit_function | function函数 | 无，必选参数 | 该函数应包含一个参数以接收Object消息数据进行处理 |

### 绑定论坛事件

-   用作绑定接收论坛事件的函数，一般仅私域机器人能注册此事件

-   接收`FORUM_THREAD_CREATE` `FORUM_THREAD_UPDATE` `FORUM_THREAD_DELETE`

-   虽官方文档显示有其他事件，但经过实测目前尚不能接收，只能接收上述三个事件

```python
def forum_function(data):   # 可使用 def msg_function(data: Model.FORUMS_EVENT): 调用模型数据
	"""
	这是接收论坛事件的函数，包含了一个data的参数以接收Object类型数据
	:param data: 可从model取用模型数据，方法 —— data: Model.FORUMS_EVENT
	"""
	if data.t == 'FORUM_THREAD_CREATE':
		title = data.thread_info.title.paragraphs[0].elems[0].text.text
        content = ''
        for items in data.thread_info.content.paragraphs:
            d = items.elems[0]
            if d:
                if d.type == 1:
                    content += d.text.text
                elif d.type == 4:
                    content += f'{d.url.desc}（链接：{d.url.url}）'
        bot.logger.info(f'收到了一条新帖子！\n标题：{title}\n内容：{content}')


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_forum(on_forum_function=forum_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_forum()
```

| 参数                |            |        |                             |
| ----------------- | ---------- | ------ | --------------------------- |
| 字段名               | 类型         | 默认值    | 说明                          |
| on_forum_function | function函数 | 无，必选参数 | 该函数应包含一个参数以接收Object消息数据进行处理 |

### 绑定音频事件

-   用作绑定接收论坛事件的函数

-   接收`AUDIO_START` `AUDIO_FINISH` `AUDIO_ON_MIC` `AUDIO_OFF_MIC`

```python
def audio_function(data):   # 可使用 def msg_function(data: Model.AUDIO_ACTION): 调用模型数据
	"""
	这是接收音频事件的函数，包含了一个data的参数以接收Object类型数据
	:param data: 可从model取用模型数据，方法 —— data: Model.AUDIO_ACTION
	"""
	if data.t == 'AUDIO_ON_MIC ':
		bot.logger.info('频道ID：%s 子频道ID：%s 已上麦' % (data.guild_id, data.channel_id))


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_audio(on_audio_function=audio_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_audio()
```

| 参数                |            |        |                             |
| ----------------- | ---------- | ------ | --------------------------- |
| 字段名               | 类型         | 默认值    | 说明                          |
| on_audio_function | function函数 | 无，必选参数 | 该函数应包含一个参数以接收Object消息数据进行处理 |

> 音频事件疑似需要先申请相关权限，或尚未开放相关事件推送

## 辅助组件

### 注册初始运行事件（SDK版本>=2.5.0支持装饰器）

-   用作注册机器人开始时运行的函数，此函数不应有无限重复（如：While True）的内容

-   例如：

```python
def start_event():
	"""
	这是一个在机器人开始运行后（成功连接后）马上执行的函数
	"""
	all_guilds = bot.get_me_guilds()
    bot.logger.info('全部频道：' + str([items['name'] + '(' + items['id'] + ')' for items in all_guilds]))
    bot.logger.info('全部频道数量：' + str(len(all_guilds)))
    for items in all_guilds:
        gi = bot.get_guild_info(items["id"])
        if 'code' in gi and str(gi['code']) == '11292':
            bot.logger.warning(items['name'] + '(' + items['id'] + ')[权限不足，无法查询此频道信息]')
        else:
            bot.logger.info(f'频道 {items["name"]}({items["id"]}) 的拥有者：' + str(items['owner_id']))


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.register_start_event(on_start_function=start_event)
# 路径：qg_botsdk.qg_bot.BOT().register_start_event()
```

| 参数                |            |        |             |
| ----------------- | ---------- | ------ | ----------- |
| 字段名               | 类型         | 默认值    | 说明          |
| on_start_function | function函数 | 无，必选参数 | 该函数不应包含任何参数 |

### 注册循环运行事件（SDK版本>=2.5.0支持装饰器）

-   用作注册重复事件的函数，注册并开始机器人后，会根据间隔时间不断调用注册的函数

-   例如：

```python
def loop_event():
    """
    这是一个在机器人开始运行后，不断重复运行的函数
    """
    print('由于check_interval的值是60，代表每一分钟会运行函数并输出一次此段文字')


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.register_repeat_event(time_function=loop_event, check_interval=60)
# 路径：qg_botsdk.qg_bot.BOT().register_repeat_event()
```

| 参数             |              |        |                       |
| -------------- | ------------ | ------ | --------------------- |
| 字段名            | 类型           | 默认值    | 说明                    |
| time_function  | function函数   | 无，必选参数 | 该函数不应包含任何参数           |
| check_interval | int or float | 10     | 每多少秒检查调用一次时间事件函数，默认10 |

### 使用腾讯内容检测接口

-   用作检测文本内容有无疑似违规的内容

-   腾讯小程序侧内容安全检测接口，使用此接口必须使用security_setup填入小程序ID和secret

```python
# 同步sync版调用方法
def msg_function(data: MESSAGE):
	if bot.api.security_check(data.content):
		print('检测通过，内容并无违规')
	else:
		print('检测不通过，内容有违规'
)


bot = BOT(bot_id='xxx', bot_token='xxx', bot_secret='xxx')
bot.security_setup(mini_id='xxx', mini_secret='xxx')
bot.bind_msg(on_msg_function=msg_function)


# 异步async版调用方法
async def msg_function(data: MESSAGE):
	checking = await bot.api.security_check(data.content)
	if checking:
		print('检测通过，内容并无违规')
	else:
		print('检测不通过，内容有违规'
)


bot = BOT(bot_id='xxx', bot_token='xxx', bot_secret='xxx')
bot.security_setup(mini_id='xxx', mini_secret='xxx')
bot.bind_msg(on_msg_function=msg_function)


# 路径（v2.2.0后）：qg_botsdk.qg_bot.BOT().api.security_check()
# 路径（v2.2.0前）：qg_botsdk.qg_bot.BOT().security_check()
```

| 参数      |        |        |          |
| ------- | ------ | ------ | -------- |
| 字段名     | 类型     | 默认值    | 说明       |
| content | string | 无，必选参数 | 需检测的内容文本 |

| 返回    |                      |
| ----- | -------------------- |
| 返回值类型 | 说明                   |
| bool  | 检测通过返回True，否则返回False |

### logger 日志打印

-   用作记录机器人运行时的状态、运行记录等

-   sdk版本v2.2.1或以上增加了带颜色的日志输出

-   用法：

```python
def msg_function(data: MESSAGE):
	if bot.security_check(data.content):
		bot.logger.info('检测通过，内容并无违规')   # bot.logger
	else:
		bot.logger.warning('检测不通过，内容有违规'
)   # bot.logger


bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_msg(on_msg_function=msg_function)
# 路径：qg_botsdk.qg_bot.BOT().logger()
```

-   如上，SDK已内置了一个根据机器人ID信息创建的独立日志，具体log文件架构如下：

```text
你项目的主目录/
├── log/
|   ├── 第一个机器人的ID/
|   |   ├── 05_07.log
|   |   ├── 05_08.log
|   ├── 第二个机器人的ID/
|   |   ├── 05_07.log
|   |   ├── 05_08.log
```

-   同时，SDK提供的logger拥有四个等级的日志：

| 日志等级    | 说明             |
| ------- | -------------- |
| debug   | 只会写入log文件中     |
| info    | 即时显示，并写入log文件中 |
| warning | 即时显示，并写入log文件中 |
| error   | 即时显示，并写入log文件中 |

-   可使用logger记录机器人运行期间的bug或记录用户输入等，具体用法如下：

```python
def test():
	bot.logger.debug('这是debug级别的日志')   # 路径：qg_botsdk.qg_bot.BOT().logger().debug()
	bot.logger.info('这是info级别的日志')   # 路径：qg_botsdk.qg_bot.BOT().logger().info()
	bot.logger.warning('这是warning级别的日志')   # 路径：qg_botsdk.qg_bot.BOT().logger().warning()
	bot.logger.error('这是error级别的日志')   # 路径：qg_botsdk.qg_bot.BOT().logger().error()


bot = BOT(bot_id='xxx', bot_token='xxx')
test()
```

-   如不喜欢现有的格式，sdk也提供了更改格式的选项（需求sdk版本v2.1.1或以上，且sdk版本v2.2.1或以上新增了单独修改每一个level格式的方法）：

```python
# sdk版本v2.2.1或以上
bot.logger.set_formatter(
debug_format: str, info_format: str, warning_format: str,error_format: str, date_format: str
)
# 格式具体例子（把info层级日志的绿色改成蓝色）：
bot.logger.set_formatter(info_format='\033[1;34m[%(asctime)s] [%(levelname)s]\033[0m %(message)s')


# sdk版本v2.1.1 - v2.2.0
bot.logger.set_formatter(str_format: str, date_format: str)
# 格式具体例子：
bot.logger.set_formatter(str_format='[%(asctime)s] [%(levelname)s](%(name)s): %(message)s', date_format='%m-%d %H:%M:%S'）

# 具体路径：qg_botsdk.qg_bot.BOT().logger().set_formatter()
```

> 关于格式的具体写法，可参阅python的logging库：

> <https://docs.python.org/zh-cn/3/library/logging.html##logging.Formatter>

> <https://docs.python.org/zh-cn/3.6/library/logging.html##logrecord-attributes>
