# SDK 组件

本内容将介绍 SDK 核心类内提供的组件内容。

## 引言-SDK 组件

让我们先重温一下简单的工作流：

```python
from qg_botsdk import BOT

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_msg(deliver)
bot.start()
```

在这个工作流中，我们可以看到 SDK 的核心类就是 qg_botsdk.qg_bot. BOT，因此 SDK 的组件均是在这个核心类之下的应用，而核心类会分为三个部分：主要组件、绑定组件、辅助组件、API 组件。

## 主要组件

### 实例化机器人

- 以实例化注册机器人，支持同程序用多个进程注册多个机器人

```python
from qg_botsdk import BOT

BOT(bot_id='xxx', bot_token='xxx')
```

| BOT                   |         |                   |                                                                                                          |
| --------------------- | ------- | ----------------- | -------------------------------------------------------------------------------------------------------- |
| 字段名                | 类型    | 默认值            | 说明                                                                                                     |
| bot_id                | string  | 无，必选参数      | 机器人平台 BotAppID                                                                                      |
| bot_token             | string  | 无，必选参数      | 机器人平台机器人令牌                                                                                     |
| bot_secret            | string  | None              | 机器人平台机器人密钥                                                                                     |
| is_private            | bool    | False             | 是否私域机器人，默认为公域（只订阅艾特消息，不订阅全部）                                                 |
| is_sandbox            | bool    | False             | 是否开启沙箱环境测试                                                                                     |
| max_shard             | int     | 5                 | 最大分片数限制（SDK 版本 2.3.1 后已遗弃，转为自定义 shard_no 以及 total_shard）                          |
| no_permission_warning | bool    | True              | 是否开启当机器人获取疑似权限不足的事件时的警告提示，默认开启                                             |
| is_async              | bool    | False             | 使用同步 api 还是异步 api，默认 False（使用同步）                                                        |
| is_retry              | bool    | True              | 使用 api 时，如遇可重试的错误码是否自动进行重试（需求 SDK 版本>=2.2.8）                                  |
| is_log_error          | bool    | True              | 使用 api 时，如返回的结果为不成功，可自动 log 输出报错信息（需求 SDK 版本>=2.2.10）                      |
| max_workers           | int     | None              | 在同步模式下，允许同时运行的最大线程数（需求 SDK 版本>=2.3.5）                                           |
| api_max_concurrency   | int     | 0                 | API 允许的最大并发数，超过此并发数将进入队列，如此数值&lt; =0 代表不开启任何队列（需求 SDK 版本>=2.5.6） |
| api_timeout           | int     | 20                | API 请求的超时设置（需求 SDK 版本>=2.6.3）                                                               |
| protocol              | Proto   | Proto.websocket() | 机器人连接协议（需求 SDK 版本>=4.2.0）                                                                   |
| sandbox               | SandBox | None              | 沙箱环境配置（需求 SDK 版本>=4.3.1）                                                                     |

### Proto 类 （需求 SDK 版本>=4.2.0）

```python
from qg_botsdk import Proto
```

- Proto 类用于定义机器人的连接协议方式，包含三个工厂方法：
  - `Proto.websocket()`：使用 WebSocket 连接协议
  - `Proto.webhook()`：使用 Webhook 连接协议，并创建一个反向 WebSocket 供 `remote_webhook()` 方法使用
  - `Proto.remote_webhook()`：使用 WebSocket 连接到远程 Webhook 服务器的反向 WebSocket 通道

| `Proto.websocket()`               |       |        |                                                                                  |
| --------------------------------- | ----- | ------ | -------------------------------------------------------------------------------- |
| 字段名                            | 类型  | 默认值 | 说明                                                                             |
| shard_no                          | int   | 0      | 当前分片数，如不熟悉相关配置请不要轻易改动此项（需求 SDK 版本>=2.3.1）           |
| total_shard                       | int   | 1      | 最大分片数，如不熟悉相关配置请不要轻易改动此项（需求 SDK 版本>=2.3.1）           |
| disable_reconnect_on_not_recv_msg | float | 1000   | 当机器人长时间未收到消息后进行连接而非重连。默认 1000 秒（需求 SDK 版本>=3.0.0） |

| `Proto.webhook()`    |             |              |                                                                        |
| -------------------- | ----------- | ------------ | ---------------------------------------------------------------------- |
| 字段名               | 类型        | 默认值       | 说明                                                                   |
| path_to_ssl_cert     | str \| None | 无，必选参数 | SSL 证书路径，如使用了如 nginx 等反向代理方法处理 https，可填 None     |
| path_to_ssl_cert_key | str \| None | 无，必选参数 | SSL 证书密钥路径，如使用了如 nginx 等反向代理方法处理 https，可填 None |
| port                 | int         | 无，必选参数 | webhook 挂载的本机端口                                                 |
| path                 | str         | '/'          | webhook 挂载的路径                                                     |

| `Proto.remote_webhook()` |      |              |                     |
| ------------------------ | ---- | ------------ | ------------------- |
| 字段名                   | 类型 | 默认值       | 说明                |
| ws_url                   | str  | 无，必选参数 | 远程 WebHook 的 URL |

> `Proto.remote_webhook()` 方法用于连接到远程 WebHook 服务器的反向 WebSocket 通道。
>
> 由于安全理由，避免在非本地环境传输敏感信息，需要在远程服务端配置机器人基本信息后，本地进行连接。

### SandBox 类 （需求 SDK 版本>=4.3.1）

```python
from qg_botsdk import SandBox
```

- SandBox 类用于定义机器人的沙箱环境配置（非官方，仅为 SDK 内部实现）
- 当`BOT(..., is_sandbox=True)`时，只有此 Sandbox 实例指定的频道、群、用户可以接收到消息
- 当`BOT(..., is_sandbox=False)`时，过滤掉此 Sandbox 实例指定的频道、群、用户的消息

| SandBox             |                   |        |                                                                  |
| ------------------- | ----------------- | ------ | ---------------------------------------------------------------- |
| 字段名              | 类型              | 默认值 | 说明                                                             |
| guilds              | List[str] \| None | None   | 设置为沙箱的频道 ID 列表                                         |
| guild_users         | List[str] \| None | None   | 设置为沙箱的频道私信用户 ID 列表                                 |
| groups              | List[str] \| None | None   | 设置为沙箱的群 ID 列表                                           |
| q_users             | List[str] \| None | None   | 设置为沙箱的 QQ 私信用户 ID 列表                                 |
| sandbox_fail_action | bool              | True   | 沙箱模式检查失败时的处理方式，默认为放行（需求 SDK 版本>=4.3.2） |

### 开始机器人

- 开始运行实例化后的机器人，在唤起此函数后的代码将不能运行，如需非阻塞性运行，请传入 is_blocking=False

```python
bot.start()
# 路径：qg_botsdk.BOT().start()
```

| 参数        |      |        |                                                                                                                                |
| ----------- | ---- | ------ | ------------------------------------------------------------------------------------------------------------------------------ |
| 字段名      | 类型 | 默认值 | 说明                                                                                                                           |
| is_blocking | bool | True   | 机器人是否阻塞运行，如选择 False，机器人将以异步任务的方式非阻塞性运行，如不熟悉异步编程请不要使用此项（需求 SDK 版本>=2.6.0） |

### 阻塞机器人进程（需求 SDK 版本>=2.6.0）

- 当 BOT.start()选择 is_blocking=False 的非阻塞性运行时，此函数能在后续阻塞主进程而继续运行机器人，具体用例可参考<https://github.com/GLGDLY/qg_botsdk/tree/master/example/example_14(%E9%9D%9E%E9%98%BB%E5%A1%9E%E6%80%A7%E8%BF%90%E8%A1%8C).py>

```python
bot.block()
# 路径：qg_botsdk.BOT().block()
```

> 无参数

### 结束机器人

- 结束运行中的机器人

```python
bot.close()
# 路径：qg_botsdk.BOT().close()
```

> 无参数

### 获取机器人信息（需求 SDK 版本>=2.3.2）

- 获取 id（机器人的频道用户 id）、username、avatar 等机器人的频道资料

```yaml
bot.robot:
  - bot.robot.id
  - bot.username
  - bot.avatar
# 路径：qg_botsdk.BOT().robot.id/username/avatar
```

> 无参数

### 获取 SDK 内置锁（需求 SDK 版本>=2.4.3）

- 返回 SDK 内置锁（根据 SDK 并发配置分配 thread 或 async 的 Lock）

```yaml
bot.lock
# 路径：qg_botsdk.BOT().lock
```

> 无参数

### 预处理器装饰器（需求 SDK 版本>=2.5.0）

- 预处理器装饰器。用于快速注册消息预处理器

```python
@bot.before_command()
def preprocessor(data: Model.MESSAGE):
    bot.logger.info(f"收到来自{data.author.username}的消息：{data.treated_msg}")
# 路径：qg_botsdk.BOT().before_command
```

| 参数         |                                                                                                          |                                                 |                                                           |
| ------------ | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | --------------------------------------------------------- |
| 字段名       | 类型                                                                                                     | 默认值                                          | 说明                                                      |
| valid_scenes | [CommandValidScenes](https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#botcommandobject) | CommandValidScenes.GUILD\|CommandValidScenes.DM | 此处理器的有效场景，可传入多个场景 (需求 SDK 版本>=4.1.4) |

### 指令装饰器（需求 SDK 版本>=2.5.0）

- 指令装饰器。用于快速注册消息事件

```python
@bot.on_command(command='c_0')
def c_0(data: Model.MESSAGE):
    data.reply('消息包含c_0可触发此函数')
# 路径：qg_botsdk.BOT().on_command
```

| 参数                    |                                                                                                          |                                                 |                                                                                                        |
| ----------------------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 字段名                  | 类型                                                                                                     | 默认值                                          | 说明                                                                                                   |
| command                 | List[str], str                                                                                           | None                                            | 可触发事件的指令列表，与正则 regex 互斥，优先使用此项                                                  |
| regex                   | Pattern, str                                                                                             | None                                            | 可触发指令的正则 compile 实例或正则表达式，与指令表互斥                                                |
| is_require_at           | bool                                                                                                     | False                                           | 是否要求必须艾特机器人才能触发指令                                                                     |
| is_short_circuit        | bool                                                                                                     | False                                           | 如果触发指令成功是否短路不运行后续指令（将根据注册顺序和 command 先 regex 后排序指令的短路机制）       |
| is_custom_short_circuit | bool                                                                                                     | False                                           | 如果触发指令成功而回调函数返回 True 则不运行后续指令，存在时优先于 is_short_circuit                    |
| is_require_admin        | bool                                                                                                     | False                                           | 是否要求频道主或或管理才可触发指令                                                                     |
| admin_error_msg         | str                                                                                                      | None                                            | 当 is_require_admin 为 True，而触发用户的权限不足时，如此项不为 None，返回此消息并短路；否则不进行短路 |
| valid_scenes            | [CommandValidScenes](https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#botcommandobject) | CommandValidScenes.GUILD\|CommandValidScenes.DM | 此处理器的有效场景，可传入多个场景 (需求 SDK 版本>=4.1.4)                                              |

> （更多相关例子可参阅<https://github.com/GLGDLY/qg_botsdk/tree/master/example/example_13(%E8%A3%85%E9%A5%B0%E5%99%A8).py>）

### 获取当前机器人的指令列表（需求 SDK 版本>=3.0.0）

- 获取当前机器人的指令列表

```python
bot.get_current_commands()
```

| 返回                                                                                                         |                                        |
| ------------------------------------------------------------------------------------------------------------ | -------------------------------------- |
| 类型                                                                                                         | 说明                                   |
| list[[BotCommandObject](https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#botcommandobject)] | 包含机器人指令 BotCommandObject 的列表 |

> 无参数

### 获取当前机器人的预处理器列表（需求 SDK 版本>=3.0.0）

- 获取当前机器人的预处理器列表

```python
bot.get_current_preprocessors()
```

> 无参数

### 删除指令（需求 SDK 版本>=3.0.0）

- 删除指令

```python
bot.remove_command(command_obj=xxx)
```

| 参数        |                                                                                                        |        |          |
| ----------- | ------------------------------------------------------------------------------------------------------ | ------ | -------- |
| 字段名      | 类型                                                                                                   | 默认值 | 说明     |
| command_obj | [BotCommandObject](https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#botcommandobject) | None   | 指令对象 |

### 删除预处理器（需求 SDK 版本>=3.0.0）

- 删除预处理器

```python
bot.remove_preprocessor(preprocessor=xxx)
```

| 参数         |                                |        |                                |
| ------------ | ------------------------------ | ------ | ------------------------------ |
| 字段名       | 类型                           | 默认值 | 说明                           |
| preprocessor | Callable[[Model.MESSAGE], Any] | None   | 相应预处理器（注册的回调函数） |

### 加载默认消息日志模块（需求 SDK 版本>=2.6.0）

- 加载默认的消息日志模块，可以默认格式自动 log 记录接收到的用户消息

```yaml
bot.load_default_msg_logger()
# 路径：qg_botsdk.BOT().load_default_msg_logger()
```

> 无参数

### 加载插件（需求 SDK 版本>=2.5.0）

- 用于加载插件到当前机器人实例

```python
bot.load_plugins(path_to_plugins="xxx")
```

| 参数            | 类型 | 默认值 | 说明                                 |
| --------------- | ---- | ------ | ------------------------------------ |
| 字段名          | 类型 | 默认值 | 说明                                 |
| path_to_plugins | str  | None   | 指向相应.py 插件文件的相对或绝对路径 |

> （更多相关例子可参阅<https://github.com/GLGDLY/qg_botsdk/tree/master/example/example_13(%E8%A3%85%E9%A5%B0%E5%99%A8).py>）

### 清除当前所有插件、指令、预处理器（需求 SDK 版本>=3.0.0）

- 清除当前所有插件、指令、预处理器

```python
bot.clear_current_plugins()
```

> 无参数

### 更新当前机器人实例的插件（需求 SDK 版本>=3.0.0）

- 更新当前机器人实例的插件

```python
bot.refresh_plugins()
```

> 无参数

## 绑定回调函数组件（SDK 版本>=2.5.0 支持装饰器）

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

- 用作绑定接收消息的函数，将根据机器人是否公域自动判断接收艾特或所有消息

- 接收`AT_MESSAGE_CREATE` `MESSAGE_CREATE` (Model-MESSAGE: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#message>)

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
bot.bind_msg(callback=msg_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_msg()
```

| 参数         |               |              |                                                                                 |
| ------------ | ------------- | ------------ | ------------------------------------------------------------------------------- |
| 字段名       | 类型          | 默认值       | 说明                                                                            |
| callback     | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理                              |
| treated_data | bool          | True         | 是否返回经转义处理的文本，如是则会在返回的 Object 中添加一个 treated_msg 的子类 |
| all_msg      | bool          | None         | 是否无视公私域限制，强制开启全部消息接收，默认 None（不判断此项参数）           |

> - 公域机器人只能收到@机器人的消息（AT_MESSAGE_CREATE）；私域机器人能收到频道内所有消息（MESSAGE_CREATE）

> - 此绑定组件通过注册机器人时 is_private 判断公域私域，再自动判断订阅哪一种消息类型。

> - treated_msg 会自动去除开头@机器人的字段、/ 的字段等，如不想使用此功能，可直接使用 `data.content` 获取未经处理的数据

### 绑定接收私信消息事件

- 用作绑定接收私信消息的函数

- 接收`DIRECT_MESSAGE_CREATE` (Model-DIRECT_MESSAGE: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#direct-message>)

```python
def dm_function(data):   # 可使用 def msg_function(data: Model.DIRECT_MESSAGE): 调用模型数据
 """
 这是接收私信的函数，包含了一个data的参数以接收Object类型数据
 :param data: 可从model取用模型数据，方法 —— data: Model.DIRECT_MESSAGE
 """
 print('收到了消息： %s ！' % data.treated_msg)

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_dm(callback=dm_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_dm()
```

| 参数         |               |              |                                                                                 |
| ------------ | ------------- | ------------ | ------------------------------------------------------------------------------- |
| 字段名       | 类型          | 默认值       | 说明                                                                            |
| callback     | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理                              |
| treated_data | bool          | True         | 是否返回经转义处理的文本，如是则会在返回的 Object 中添加一个 treated_msg 的子类 |

> - treated_msg 会自动去除开头@机器人的字段、/ 的字段等，如不想使用此功能，可直接使用 `data.content` 获取未经处理的数据

### 绑定撤回消息事件

- 用作绑定接收消息撤回事件的函数，注册时将自动根据公域私域注册艾特或全部消息，但不会主动注册私信事件

- 接收`MESSAGE_DELETE` `PUBLIC_MESSAGE_DELETE` `DIRECT_MESSAGE_DELETE` (Model-MESSAGE_DELETE: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#message-delete>)

```python
def delete_function(data):   # 可使用 def msg_function(data: Model.MESSAGE_DELETE): 调用模型数据
 """
 这是接收撤回事件的函数，包含了一个data的参数以接收Object类型数据
 :param data: 可从model取用模型数据，方法 —— data: Model.MESSAGE_DELETE
 """
 print('ID：%s 的用户撤回了用户 %s(ID：%s)的消息【%s】' % (
        data.op_user.id, data.message.author.username, data.message.author.id, data.message.channel_id))

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_msg_delete(callback=delete_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_msg_delete()
```

| 参数         |               |              |                                                                                 |
| ------------ | ------------- | ------------ | ------------------------------------------------------------------------------- |
| 字段名       | 类型          | 默认值       | 说明                                                                            |
| callback     | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理                              |
| treated_data | bool          | True         | 是否返回经转义处理的文本，如是则会在返回的 Object 中添加一个 treated_msg 的子类 |

> 如绑定了私信事件，撤回消息事件则将包含私信的撤回消息（DIRECT_MESSAGE_DELETE）

### 绑定频道事件

- 用作绑定接收频道信息的函数

- 接收`GUILD_CREATE` `GUILD_UPDATE` `GUILD_DELETE` (Model-GUILDS: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#guilds>)

- 【`CHANNEL_CREATE` `CHANNEL_UPDATE` `CHANNEL_DELETE`】-> \*\*\*注意 SDK 版本 v2.2.4 后，此项不再接收 channel 事件，改为下方【绑定子频道事件】进行接收 (Model-CHANNELS: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#channels-sdkv2-2-4>)

```python
def guild_function(data):   # 可使用 def msg_function(data: GUILDS): 调用模型数据
 """
 这是接收频道事件的函数，包含了一个data的参数以接收Object类型数据
 :param data: 可从model取用模型数据，方法 —— data: Model.GUILDS
 """
 print('收到了来自频道 %s（ID:%s） 的数据更新：%s' % (
data.name, data.id, data.t))  # data.t代表接收的事件名，如GUILD_CREATE

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_guild_event(callback=guild_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_guild_event()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

### 绑定子频道事件（需求 sdk 版本 ≥v2.2.4）

- 用作绑定接收子频道信息的函数

- 接收`CHANNEL_CREATE` `CHANNEL_UPDATE` `CHANNEL_DELETE` (Model-CHANNELS: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#channels-sdkv2-2-4>)

```python
def channel_function(data):   # 可使用 def msg_function(data: Model.CHANNELS): 调用模型数据
 """
 这是接收频道事件的函数，包含了一个data的参数以接收Object类型数据
 :param data: 可从model取用模型数据，方法 —— data: Model.CHANNELS
 """
 print('收到了来自子频道 %s（ID:%s） 的数据更新：%s' % (
data.name, data.id, data.t))  # data.t代表接收的事件名，如CHANNEL_CREATE

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_channel_event(callback=channel_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_channel_event()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

### 绑定频道成员

- 用作绑定接收频道信息的函数

- 接收`GUILD_MEMBER_ADD` `GUILD_MEMBER_UPDATE` `GUILD_MEMBER_REMOVE` (Model-GUILD_MEMBERS: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#guild-members>)

```python
def guild_member_function(data):   # 可使用 def msg_function(data: Model.GUILD_MEMBERS): 调用模型数据
 """
 这是接收频道成员事件的函数，包含了一个data的参数以接收Object类型数据
 :param data: 可从model取用模型数据，方法 —— data: Model.GUILD_MEMBERS
 """
 print('收到了来自频道ID:%s 的成员 %s 的数据更新：%s' % (
data.id, data.user.username, data.t))

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_guild_member(callback=guild_member_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_guild_member()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

### 绑定表情表态事件

- 用作绑定接收表情表态信息的函数

- 接收`MESSAGE_REACTION_ADD` `MESSAGE_REACTION_REMOVE` (Model-REACTION: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#reaction>)

```python
def reaction_function(data):   # 可使用 def msg_function(data: Model.REACTION): 调用模型数据
 """
 这是接收表情表态事件的函数，包含了一个data的参数以接收Object类型数据
 :param data: 可从model取用模型数据，方法 —— data: Model.REACTION
 """
 if data.t == 'MESSAGE_REACTION_ADD':
  bot.api.send_msg('%s 在频道 %s 子频道 %s 新增了新的表情动态！' % (data.user_id, data.guild_id, data.channel_id))

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_reaction(callback=reaction_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_reaction()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

### 绑定互动事件

- 用作绑定接收互动事件的函数，当前未有录入数据结构

- 接收`INTERACTION_CREATE` (Model-INTERACTION: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#interaction>)

```python
def interaction_function(data):
 """
 这是接收互动事件的函数，包含了一个data的参数以接收Object类型数据
 :param data: 当前未有录入数据结构
 """
 print('暂时未有数据结构记录')

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_interaction(callback=interaction_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_interaction()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

### 绑定审核事件

- 用作绑定接收审核事件的函数

- 接收`MESSAGE_AUDIT_PASS` `MESSAGE_AUDIT_REJECT` (Model-MESSAGE_AUDIT: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#message-audit>)

```python
def audit_function(data):   # 可使用 def msg_function(data: Model.MESSAGE_AUDIT): 调用模型数据
 """
 这是接收审核事件的函数，包含了一个data的参数以接收Object类型数据
 :param data: 可从model取用模型数据，方法 —— data: Model.MESSAGE_AUDIT
 """
 if data.t == 'MESSAGE_AUDIT_PASS':
  bot.logger.info('主动消息审核通过啦，已自动发往子频道%s了！' % data.channel_id)

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_audit(callback=audit_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_audit()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

### 绑定论坛事件

- 用作绑定接收论坛事件的函数，一般仅私域机器人能注册此事件

- 接收`FORUM_THREAD_CREATE` `FORUM_THREAD_UPDATE` `FORUM_THREAD_DELETE` (Model-FORUMS_EVENT: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#forums-event>)

- 虽官方文档显示有其他事件，但经过实测目前尚不能接收，只能接收上述三个事件

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
bot.bind_forum(callback=forum_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_forum()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

### 绑定公域论坛事件

- 用作绑定接收公域版本的论坛事件的函数

- 接收`OPEN_FORUM_THREAD_CREATE` `OPEN_FORUM_THREAD_UPDATE` `OPEN_FORUM_THREAD_DELETE` (Model-OPEN_FORUMS: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#open-forums>)

- 虽官方文档显示有其他事件，但经过实测目前尚不能接收，只能接收上述三个事件

```python
def open_forum_function(data):   # 可使用 def msg_function(data: Model.OPEN_FORUMS): 调用模型数据
 """
 这是接收公域论坛事件的函数，包含了一个data的参数以接收Object类型数据
 :param data: 可从model取用模型数据，方法 —— data: Model.OPEN_FORUMS
 """
 if data.t == 'OPEN_FORUM_THREAD_CREATE':
  author_id = data.author_id
        bot.logger.info(f'收到了一条新帖子！\n作者：<@{author_id}>')

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_open_forum(callback=forum_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_open_forum()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

### 绑定音频事件

- 用作绑定接收论坛事件的函数

- 接收`AUDIO_START` `AUDIO_FINISH` `AUDIO_ON_MIC` `AUDIO_OFF_MIC` (Model-AUDIO_ACTION: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#audio-action>)

```python
def audio_function(data):   # 可使用 def msg_function(data: Model.AUDIO_ACTION): 调用模型数据
 """
 这是接收音频事件的函数，包含了一个data的参数以接收Object类型数据
 :param data: 可从model取用模型数据，方法 —— data: Model.AUDIO_ACTION
 """
 if data.t == 'AUDIO_ON_MIC ':
  bot.logger.info('频道ID：%s 子频道ID：%s 已上麦' % (data.guild_id, data.channel_id))

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_audio(callback=audio_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_audio()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

> 音频事件疑似需要先申请相关权限，或尚未开放相关事件推送

### 绑定 Q 群事件（需求 SDK 版本>=4.1.0）

- 用作绑定接收 Q 群事件的函数
- 接收`GROUP_ADD_ROBOT` `GROUP_DEL_ROBOT` `GROUP_MSG_REJECT` `GROUP_MSG_RECEIVE` (Model-GROUP_EVENTS: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#group-events>)

```python
def group_function(data):   # 可使用 def msg_function(data: Model.GROUP_EVENTS): 调用模型数据
 """
 这是接收 Q 群事件的函数，包含了一个 data 的参数以接收 Object 类型数据
 :param data: 可从 model 取用模型数据，方法 —— data: Model.GROUP_EVENTS
 """
 if data.t == 'GROUP_ADD_ROBOT':
  bot.logger.info('机器人被添加到了 Q 群 %s' % data.group_openid)

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_group_event(callback=group_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_group_event()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

### 绑定 QQ 用户事件（需求 SDK 版本>=4.1.0）

- 用作绑定接收 QQ 用户事件的函数

- 接收`FRIEND_ADD` `FRIEND_DEL` `C2C_MSG_REJECT` `C2C_MSG_RECEIVE` (Model-FRIEND_EVENTS: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#friend-events>)

```python
def friend_function(data):   # 可使用 def msg_function(data: Model.FRIEND_EVENTS): 调用模型数据
 """
 这是接收 QQ 用户事件的函数，包含了一个 data 的参数以接收 Object 类型数据
 :param data: 可从 model 取用模型数据，方法 —— data: Model.FRIEND_EVENTS
 """
 if data.t == 'FRIEND_ADD':
  bot.logger.info('QQ 用户 %s 添加了机器人为好友' % data.openid)

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_friend_event(callback=friend_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_friend_event()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

### 绑定 QQ 群聊消息事件（需求 SDK 版本>=4.1.0）

- 用作绑定接收群聊消息事件的函数

- 接收`GROUP_AT_MESSAGE_CREATE` (Model-GROUP_MESSAGE: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#group-message>)

- 可参考例子：[example 16 (Q 群简单工作流)](<https://github.com/GLGDLY/qg_botsdk/blob/master/example/example_16(Q%E7%BE%A4%E7%AE%80%E5%8D%95%E5%B7%A5%E4%BD%9C%E6%B5%81).py>)

```python
def group_msg_function(data):   # 可使用 def msg_function(data: Model.GROUP_MESSAGE): 调用模型数据
 """
 这是接收群聊消息事件的函数，包含了一个 data 的参数以接收 Object 类型数据
 :param data: 可从 model 取用模型数据，方法 —— data: Model.GROUP_MESSAGE
 """
 bot.logger.info('收到了群聊消息：%s' % data.treated_msg)

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_group_msg(callback=group_msg_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_group_msg()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

### 绑定 QQ 用户消息事件（需求 SDK 版本>=4.1.0）

- 用作绑定接收用户消息事件的函数

- 接收`C2C_MESSAGE_CREATE` (Model-C2C_MESSAGE: <https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#c2c-message>)

```python
def c2c_msg_function(data):   # 可使用 def msg_function(data: Model.C2C_MESSAGE): 调用模型数据
 """
 这是接收用户消息事件的函数，包含了一个 data 的参数以接收 Object 类型数据
 :param data: 可从 model 取用模型数据，方法 —— data: Model.C2C_MESSAGE
 """
 bot.logger.info('收到了用户消息：%s' % data.treated_msg)

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_friend_msg(callback=c2c_msg_function)
# 路径：qg_botsdk.qg_bot.BOT().bind_friend_msg()
```

| 参数     |               |              |                                                    |
| -------- | ------------- | ------------ | -------------------------------------------------- |
| 字段名   | 类型          | 默认值       | 说明                                               |
| callback | function 函数 | 无，必选参数 | 该函数应包含一个参数以接收 Object 消息数据进行处理 |

## 辅助组件

### 注册初始运行事件（SDK 版本>=2.5.0 支持装饰器）

- 用作注册机器人开始时运行的函数，此函数不应有无限重复（如：While True）的内容

- 例如：

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

| 参数              |               |              |                        |
| ----------------- | ------------- | ------------ | ---------------------- |
| 字段名            | 类型          | 默认值       | 说明                   |
| on_start_function | function 函数 | 无，必选参数 | 该函数不应包含任何参数 |

### 注册循环运行事件（SDK 版本>=2.5.0 支持装饰器）

- 用作注册重复事件的函数，注册并开始机器人后，会根据间隔时间不断调用注册的函数

- 例如：

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

| 参数           |               |              |                                           |
| -------------- | ------------- | ------------ | ----------------------------------------- |
| 字段名         | 类型          | 默认值       | 说明                                      |
| time_function  | function 函数 | 无，必选参数 | 该函数不应包含任何参数                    |
| check_interval | int or float  | 10           | 每多少秒检查调用一次时间事件函数，默认 10 |

### 使用腾讯内容检测接口

- 用作检测文本内容有无疑似违规的内容

- 腾讯小程序侧内容安全检测接口，使用此接口必须使用 security_setup 填入小程序 ID 和 secret

```python
# 同步sync版调用方法
def msg_function(data: MESSAGE):
 if bot.api.security_check(data.content):
  print('检测通过，内容并无违规')
 else:
  print('检测不通过，内容有违规')

bot = BOT(bot_id='xxx', bot_token='xxx', bot_secret='xxx')
bot.security_setup(mini_id='xxx', mini_secret='xxx')
bot.bind_msg(callback=msg_function)

# 异步async版调用方法
async def msg_function(data: MESSAGE):
 checking = await bot.api.security_check(data.content)
 if checking:
  print('检测通过，内容并无违规')
 else:
  print('检测不通过，内容有违规')

bot = BOT(bot_id='xxx', bot_token='xxx', bot_secret='xxx')
bot.security_setup(mini_id='xxx', mini_secret='xxx')
bot.bind_msg(callback=msg_function)

# 路径（v2.2.0后）：qg_botsdk.qg_bot.BOT().api.security_check()
# 路径（v2.2.0前）：qg_botsdk.qg_bot.BOT().security_check()
```

| 参数    |        |              |                  |
| ------- | ------ | ------------ | ---------------- |
| 字段名  | 类型   | 默认值       | 说明             |
| content | string | 无，必选参数 | 需检测的内容文本 |

| 返回       |                                   |
| ---------- | --------------------------------- |
| 返回值类型 | 说明                              |
| bool       | 检测通过返回 True，否则返回 False |

### logger 日志打印

- 用作记录机器人运行时的状态、运行记录等

- sdk 版本 v2.2.1 或以上增加了带颜色的日志输出

- 用法：

```python
def msg_function(data: MESSAGE):
 if bot.security_check(data.content):
  bot.logger.info('检测通过，内容并无违规')   # bot.logger
 else:
  bot.logger.warning('检测不通过，内容有违规'
)   # bot.logger

bot = BOT(bot_id='xxx', bot_token='xxx')
bot.bind_msg(msg_function)
# 路径：qg_botsdk.qg_bot.BOT().logger()
```

- 如上，SDK 已内置了一个根据机器人 ID 信息创建的独立日志，具体 log 文件架构如下：

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

- 同时，SDK 提供的 logger 拥有四个等级的日志：

| 日志等级 | 说明                        |
| -------- | --------------------------- |
| debug    | 只会写入 log 文件中         |
| info     | 即时显示，并写入 log 文件中 |
| warning  | 即时显示，并写入 log 文件中 |
| error    | 即时显示，并写入 log 文件中 |

- 可使用 logger 记录机器人运行期间的 bug 或记录用户输入等，具体用法如下：

```python
def test():
 bot.logger.debug('这是debug级别的日志')   # 路径：qg_botsdk.qg_bot.BOT().logger().debug()
 bot.logger.info('这是info级别的日志')   # 路径：qg_botsdk.qg_bot.BOT().logger().info()
 bot.logger.warning('这是warning级别的日志')   # 路径：qg_botsdk.qg_bot.BOT().logger().warning()
 bot.logger.error('这是error级别的日志')   # 路径：qg_botsdk.qg_bot.BOT().logger().error()

bot = BOT(bot_id='xxx', bot_token='xxx')
test()
```

- 如不喜欢现有的格式，sdk 也提供了更改格式的选项（需求 sdk 版本 v2.1.1 或以上，且 sdk 版本 v2.2.1 或以上新增了单独修改每一个 level 格式的方法）：

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
bot.logger.set_formatter(str_format='[%(asctime)s] [%(levelname)s](%(name)s): %(message)s', date_format='%m-%d %H:%M:%S')

# 具体路径：qg_botsdk.qg_bot.BOT().logger().set_formatter()
```

> 关于格式的具体写法，可参阅 python 的 logging 库：

> <https://docs.python.org/zh-cn/3/library/logging.html##logging.Formatter>

> <https://docs.python.org/zh-cn/3.6/library/logging.html##logrecord-attributes>
