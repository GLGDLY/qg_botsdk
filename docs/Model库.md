# Model 库

qg_botsdk 提供了数据的模型数据供大家验证结构准确性，更轻易避免出现 bug 而无法运行机器人的情况。本文将带领大家粗略认识一下 model 库的应用和相关的数据结构

## Model

```python
from qg_botsdk import Model   ## 导入数据模型
```

导入后，即可透过类型提示（data: MESSAGE）的方法验证数据结构正确性：

```python
def deliver(data: Model.MESSAGE):  ## Model.MESSAGE为导入的一个数据模型
    if '你好' in data.treated_msg:
        bot.send_msg('你好，世界', data.id, data.channel_id)
```

当使用数据子项时，你使用的 IDE 理论上将会有相应的子数据结构提示：

![](image/model0.png)

而当输入错误的数据结构（正确的字段名为`channel_id`，而非`channelid`）时，你使用的 IDE 理论上将会提示错误：

![](image/model1.png)

需要注意的是，所有事件都会返回一个`event_id`的值，但只有以下事件的 event_id 可以用作发送被动消息的消息 ID：

![](image/model2.png)

### 数据结构

#### GUILDS

| 结构         |        |                                                             |
| ------------ | ------ | ----------------------------------------------------------- |
| 字段名       | 类型   | 说明                                                        |
| description  | sring  | 频道介绍                                                    |
| icon         | sring  | 频道头像图片 url                                            |
| id           | sring  | 频道 ID（guild id）                                         |
| joined_at    | sring  | 机器人加入频道时间，具体格式例如：2021-10-21T11:20:18+08:00 |
| max_members  | int    | 频道最大成员数                                              |
| member_count | int    | 频道当前成员数                                              |
| name         | string | 频道名                                                      |
| op_user_id   | string | 操作人 ID                                                   |
| owner_id     | string | 频道拥有者 ID                                               |
| t            | string | 事件类型字段，如 GUILD_CREATE                               |
| event_id     | sring  | 事件 ID                                                     |

#### CHANNELS（需求 sdk 版本 ≥v2.2.4）

| 结构             |        |                                                                  |
| ---------------- | ------ | ---------------------------------------------------------------- |
| 字段名           | 类型   | 说明                                                             |
| application_id   | sring  | 标识应用子频道应用类型                                           |
| guild_id         | sring  | 频道 ID                                                          |
| id               | sring  | 子频道 ID（channel id）                                          |
| name             | sring  | 子频道名                                                         |
| op_user_id       | string | 操作人 ID                                                        |
| owner_id         | string | 频道拥有者 ID                                                    |
| parent_id        | string | 所属分组 id，仅对子频道有效，对 子频道分组（ChannelType=4） 无效 |
| permissions      | string | 用户拥有的子频道权限                                             |
| position         | int    | 排序值                                                           |
| private_type     | int    | 子频道私密类型                                                   |
| speak_permission | int    | 子频道发言权限                                                   |
| sub_type         | int    | 子频道子类型                                                     |
| type             | int    | 子频道类型                                                       |
| t                | string | 事件类型字段，如 GUILD_CREATE                                    |
| event_id         | sring  | 事件 ID                                                          |

#### GUILD_MEMBERS

| 结构       |        |                                                               |
| ---------- | ------ | ------------------------------------------------------------- |
| 字段名     | 类型   | 说明                                                          |
| guild_id   | sring  | 频道 ID                                                       |
| joined_at  | sring  | 该成员加入频道时间，具体格式例如：2021-10-21T11:20:18+08:00   |
| nick       | string | 成员在当前频道的昵称                                          |
| roles      | list   | 该成员拥有的身份组 ID 列表，当中每个身份组 ID 的类型为 string |
| user       | object | 该成员详细信息，其子类请参阅下表【结构：user】                |
| op_user_id | string | 操作人 ID                                                     |
| t          | string | 事件类型字段，如 GUILD_CREATE                                 |
| event_id   | sring  | 事件 ID                                                       |

| 结构：user |        |                        |
| ---------- | ------ | ---------------------- |
| 字段名     | 类型   | 说明                   |
| avatar     | sring  | 该成员头像图片 url     |
| bot        | bool   | 该成员是否机器人       |
| id         | string | 该成员的 ID            |
| username   | list   | 该成员在频道全局的昵称 |

#### MESSAGE

| 结构              |        |                                                                                                        |
| ----------------- | ------ | ------------------------------------------------------------------------------------------------------ |
| 字段名            | 类型   | 说明                                                                                                   |
| author            | object | 发送消息成员自身的详细信息，其子类请参阅下表【结构：author】                                           |
| channel_id        | sring  | 子频道 ID                                                                                              |
| guild_id          | sting  | 频道 ID                                                                                                |
| content           | string | 消息内容                                                                                               |
| message_reference | object | 该条消息的引用消息数据，如没有引用则没有此字段，其子类请参阅下表【结构：message_reference】            |
| mentions          | object | 该条消息@其他成员的数据，如没有艾特则没有此字段，列表中的子类请参阅下表【结构：Mentions】              |
| attachments       | object | 该条消息的附件（图片）数据，如没有附件则没有此字段，列表中的子类请参阅下表【结构：Attachments】        |
| id                | string | 消息 ID（用于发送被动消息）                                                                            |
| seq               | int    | 用于消息间的排序，seq 在同一子频道中按从先到后的顺序递增，不同的子频道之间消息无法排序                 |
| seq_in_channel    | string | 子频道消息 seq，用于消息间的排序，seq 在同一子频道中按从先到后的顺序递增，不同的子频道之间消息无法排序 |
| timestamp         | string | 消息创建时间（ISO8601 timestamp）                                                                      |
| tts               | bool   | 未知详情，疑似 text-to-speech 语音合成（该字段不稳定出现，请勿用于运营应用环境）                       |
| pinned            | bool   | 该消息是否精华消息（该字段不稳定出现，请勿用于运营应用环境）                                           |
| type              | sring  | 未知详情，疑似消息类型（该字段不稳定出现，请勿用于运营应用环境）                                       |
| flags             | sring  | 未知详情（该字段不稳定出现，请勿用于运营应用环境）                                                     |
| t                 | string | 事件类型字段，如 GUILD_CREATE                                                                          |
| event_id          | sring  | 事件 ID                                                                                                |
| member            | object | 发送消息成员在频道的详细信息，其子类请参阅下表【结构：member】                                         |
| treated_msg       | string | 经过处理（包括去除艾特机器人、/等字段）的内容（绑定事件时 treated_data=False 则没有此字段）            |

| 结构：author |        |                        |
| ------------ | ------ | ---------------------- |
| 字段名       | 类型   | 说明                   |
| avatar       | sring  | 该成员头像图片 url     |
| bot          | bool   | 该成员是否机器人       |
| id           | string | 该成员的 ID            |
| username     | list   | 该成员在频道全局的昵称 |

| 结构：message_reference |       |                     |
| ----------------------- | ----- | ------------------- |
| 字段名                  | 类型  | 说明                |
| message_id              | sring | 被引用消息的消息 ID |

| 结构：Mentions |        |                         |
| -------------- | ------ | ----------------------- |
| 字段名         | 类型   | 说明                    |
| avatar         | sring  | 被@成员头像图片 url     |
| bot            | bool   | 被@成员是否机器人       |
| id             | string | 被@成员的 ID            |
| username       | list   | 被@成员在频道全局的昵称 |

| 结构：Attachments |        |                                  |
| ----------------- | ------ | -------------------------------- |
| 字段名            | 类型   | 说明                             |
| content_type      | sring  | 附件类型，如：image/jpeg         |
| filename          | string | 附件名，如：504BA0……6A509E68.jpg |
| height            | int    | 高度                             |
| width             | int    | 宽度                             |
| size              | int    | 附件大小                         |
| id                | string | 附件 ID                          |
| url               | string | 附件 url                         |

| 结构：member |      |                         |
| ------------ | ---- | ----------------------- |
| 字段名       | 类型 | 说明                    |
| joined_at    | str  | 用户加入频道的时间      |
| nick         | str  | 用户的昵称              |
| roles        | list | 用户在频道内的身份组 ID |

#### DIRECT_MESSAGE

| 结构              |        |                                                                                                        |
| ----------------- | ------ | ------------------------------------------------------------------------------------------------------ |
| 字段名            | 类型   | 说明                                                                                                   |
| author            | object | 发送消息成员的详细信息，其子类请参阅下表【结构：author】                                               |
| channel_id        | sring  | 子频道 ID                                                                                              |
| guild_id          | sting  | 频道 ID                                                                                                |
| content           | string | 消息内容                                                                                               |
| message_reference | object | 该条消息的引用消息数据，如没有引用则没有此字段，其子类请参阅下表【结构：message_reference】            |
| attachments       | object | 该条消息的附件（图片）数据，如没有附件则没有此字段，列表中的子类请参阅下表【结构：Attachments】        |
| id                | string | 消息 ID（用于发送被动消息）                                                                            |
| seq               | int    | 用于消息间的排序，seq 在同一子频道中按从先到后的顺序递增，不同的子频道之间消息无法排序                 |
| seq_in_channel    | string | 子频道消息 seq，用于消息间的排序，seq 在同一子频道中按从先到后的顺序递增，不同的子频道之间消息无法排序 |
| src_guild_id      | string | 用于私信场景下识别真实的来源频道 id                                                                    |
| timestamp         | string | 消息创建时间（ISO8601 timestamp）                                                                      |
| t                 | string | 事件类型字段，如 GUILD_CREATE                                                                          |
| event_id          | sring  | 事件 ID                                                                                                |
| treated_msg       | string | 经过处理（包括去除艾特机器人、/等字段）的内容（绑定事件时 treated_data=False 则没有此字段）            |

| 结构：author |        |                        |
| ------------ | ------ | ---------------------- |
| 字段名       | 类型   | 说明                   |
| avatar       | sring  | 该成员头像图片 url     |
| bot          | bool   | 该成员是否机器人       |
| id           | string | 该成员的 ID            |
| username     | list   | 该成员在频道全局的昵称 |

| 结构：message_reference |       |                     |
| ----------------------- | ----- | ------------------- |
| 字段名                  | 类型  | 说明                |
| message_id              | sring | 被引用消息的消息 ID |

| 结构：Attachments |        |                                  |
| ----------------- | ------ | -------------------------------- |
| 字段名            | 类型   | 说明                             |
| content_type      | sring  | 附件类型，如：image/jpeg         |
| filename          | string | 附件名，如：504BA0……6A509E68.jpg |
| height            | int    | 高度                             |
| width             | int    | 宽度                             |
| size              | int    | 附件大小                         |
| id                | string | 附件 ID                          |
| url               | string | 附件 url                         |

#### MESSAGE_DELETE

| 结构     |        |                                                         |
| -------- | ------ | ------------------------------------------------------- |
| 字段名   | 类型   | 说明                                                    |
| message  | object | 被撤回消息的消息数据，其子类请参阅下表【结构：message】 |
| op_user  | object | 操作人数据，其子类只有 id（类型为 string）              |
| t        | string | 事件类型字段，如 GUILD_CREATE                           |
| event_id | sring  | 事件 ID                                                 |

| 结构：message |        |                                                        |
| ------------- | ------ | ------------------------------------------------------ |
| 字段名        | 类型   | 说明                                                   |
| author        | object | 被撤回消息的作者数据，其子类请参阅下表【结构：author】 |
| id            | string | 被撤回消息的消息 ID                                    |
| channel_id    | string | 子频道 ID                                              |
| guild_id      | string | 频道 ID                                                |

| 结构：author |        |                  |
| ------------ | ------ | ---------------- |
| 字段名       | 类型   | 说明             |
| bot          | bool   | 该成员是否机器人 |
| id           | string | 该成员 ID        |
| username     | string | 该成员昵称       |

#### MESSAGE_AUDIT

| 结构        |        |                                                           |
| ----------- | ------ | --------------------------------------------------------- |
| 字段名      | 类型   | 说明                                                      |
| audit_id    | string | 消息审核 ID                                               |
| audit_time  | string | 消息审核时间（ISO8601 timestamp）                         |
| create_time | string | 消息创建时间（ISO8601 timestamp）                         |
| channel_id  | string | 子频道 ID                                                 |
| guild_id    | string | 频道 ID                                                   |
| message_id  | string | 成功后的消息 ID（只有审核通过事件才会有 message_id 的值） |
| t           | string | 事件类型字段，如 GUILD_CREATE                             |
| event_id    | sring  | 事件 ID                                                   |

#### FORUMS_EVENT

- 官方目前仍在开发此事件，目前的字段存在许多冗余，因此后续很有可能随时出现变化。

- 如遇到官方更改字段的相关情况，请马上 [联系作者](/联系与反馈) 进行修改，后下载最新 release 使用>

- `thread_info`字段较为复杂，具体可视化结构如下：

```text
thread_info
├── title
|   ├── paragraphs (list)
|   |   ├── elems (list)
|   |   |   ├── type
|   |   |   ├── text
|   |   |   |   ├── text
|   |   ├── props
├── content
|   ├── paragraphs (list)
|   |   ├── elems (list)
|   |   |   ├── type
|   |   |   ├── 根据type字段判断此字段，目前可能的值：text、url、(image、video)
|   |   ├── props
```

| 结构        |        |                                                     |
| ----------- | ------ | --------------------------------------------------- |
| 字段名      | 类型   | 说明                                                |
| thread_info | object | 帖子数据详情，其子类请参阅下表【结构：thread_info】 |
| author_id   | string | 帖子作者的频道 ID                                   |
| date_time   | string | 帖子发布事件（ISO8601 timestamp）                   |
| channel_id  | string | 子频道 ID                                           |
| guild_id    | string | 频道 ID                                             |
| thread_id   | string | 帖子 ID                                             |
| t           | string | 事件类型字段，如 GUILD_CREATE                       |
| event_id    | sring  | 事件 ID                                             |

| 结构：thread_info |        |                                         |
| ----------------- | ------ | --------------------------------------- |
| 字段名            | 类型   | 说明                                    |
| title             | object | 标题数据，其子类请参阅【结构：sub_thr】 |
| content           | object | 标题数据，其子类请参阅【结构：sub_thr】 |

| 结构：sub_thr |      |                                        |
| ------------- | ---- | -------------------------------------- |
| 字段名        | 类型 | 说明                                   |
| paragraphs    | list | 段落列表，其每一项请参阅【结构：para】 |

| 结构：para |        |                                                                                  |
| ---------- | ------ | -------------------------------------------------------------------------------- |
| 字段名     | 类型   | 说明                                                                             |
| elems      | list   | 内容元素，其每一项请分别参阅——title：【结构：elems_t】content：【结构：elems_c】 |
| props      | object | 作用未名，空 object 数据                                                         |

| 结构：elems_t |        |                                    |
| ------------- | ------ | ---------------------------------- |
| 字段名        | 类型   | 说明                               |
| text          | object | 包含一个子类 text，其类型为 string |
| type          | int    | 元素类型，可能的值：1（普通文本）  |

| 结构：elems_c |        |                                                                   |
| ------------- | ------ | ----------------------------------------------------------------- |
| 字段名        | 类型   | 说明                                                              |
| text          | object | 包含一个子类 text，其类型为 string                                |
| url           | object | 包含两个子类：url desc，其类型均为 string                         |
| type          | int    | 元素类型，可能的值：1（普通文本）、2（图片）、3（视频）、4（url） |

> 现有推送和相关信息的 type 字段：

> type 1：普通文本，子字段 text

> type 2：图片，子字段 image（曾短暂出现，目前为空子字段，无任何内容反馈）

> type 3：视频，子字段 video（曾短暂出现，目前为空子字段，无任何内容反馈）

>

> type 4：url 信息，子字段 url

>

>

>

> 现无推送，根据文档列出的 type：

> 原 type 2：at 信息，目前为空子字段，无任何内容反馈

> 原 type 4：表情，目前为空子字段，无任何内容反馈

> 原 type 5：##子频道，目前为空子字段，无任何内容反馈

#### OPEN_FORUMS

- 公域版本的 FORUMS 论坛事件

| 结构       |        |                               |
| ---------- | ------ | ----------------------------- |
| 字段名     | 类型   | 说明                          |
| channel_id | string | 子频道 ID                     |
| guild_id   | string | 频道 ID                       |
| author_id  | string | 帖子作者的频道 ID             |
| t          | string | 事件类型字段，如 GUILD_CREATE |
| event_id   | sring  | 事件 ID                       |

#### AUDIO_ACTION

- 只有 AUDIO_START、AUDIO_FINISH 拥有 audio_url 和 text 字段

| 结构       |        |                               |
| ---------- | ------ | ----------------------------- |
| 字段名     | 类型   | 说明                          |
| audio_url  | string | 音频 url                      |
| text       | string | 音频描述                      |
| channel_id | string | 子频道 ID                     |
| guild_id   | string | 频道 ID                       |
| t          | string | 事件类型字段，如 GUILD_CREATE |
| event_id   | sring  | 事件 ID                       |

#### REACTION

| 结构       |        |                                                        |
| ---------- | ------ | ------------------------------------------------------ |
| 字段名     | 类型   | 说明                                                   |
| emoji      | object | 表情表态的 emoji 数据，其子类请参阅下表【结构：emoji】 |
| target     | object | 表态引用对象的数据，其子类请参阅下表【结构：target】   |
| user_id    | string | 发布表情表态的用户 ID                                  |
| channel_id | string | 子频道 ID                                              |
| guild_id   | string | 频道 ID                                                |
| t          | string | 事件类型字段，如 GUILD_CREATE                          |
| event_id   | sring  | 事件 ID                                                |

| 结构：emoji |        |          |
| ----------- | ------ | -------- |
| 字段名      | 类型   | 说明     |
| id          | string | 表情 ID  |
| type        | int    | 表情类型 |

> 表情 ID 和类型可参阅：<https://bot.q.qq.com/wiki/develop/api/openapi/emoji/model.html>

| 结构：target |        |                            |
| ------------ | ------ | -------------------------- |
| 字段名       | 类型   | 说明                       |
| id           | string | 表态对象的 ID              |
| type         | int    | 表态对象的类型（参考下图） |

表态对象类型如下：

![](image/model3.png)

#### INTERACTION

| 结构           |        |                                                    |
| -------------- | ------ | -------------------------------------------------- |
| 字段名         | 类型   | 说明                                               |
| data           | object | 互动事件的返回数据，其子类请参阅下表【结构：data】 |
| application_id | string | APP ID                                             |
| channel_id     | string | 子频道 ID                                          |
| guild_id       | string | 频道 ID                                            |
| id             | string | 未知                                               |
| type           | int    | 未知                                               |
| version        | int    | 未知                                               |
| t              | string | 事件类型字段，如 GUILD_CREATE                      |
| event_id       | sring  | 事件 ID                                            |

| 结构：data |        |                                                            |
| ---------- | ------ | ---------------------------------------------------------- |
| 字段名     | 类型   | 说明                                                       |
| resolved   | object | 互动事件的解析返回数据，其子类请参阅下表【结构：resolved】 |
| type       | int    | 未知                                                       |

| 结构：resolved |        |                       |
| -------------- | ------ | --------------------- |
| 字段名         | 类型   | 说明                  |
| button_data    | string | 按钮配置的返回数据    |
| button_id      | string | 按钮配置的按钮 ID     |
| message_id     | string | 触发按钮事件的消息 ID |
| user_id        | string | 触发按钮事件的用户 ID |

#### LIVE_CHANNEL_MEMBER

| 结构         |        |                                           |
| ------------ | ------ | ----------------------------------------- |
| 字段名       | 类型   | 说明                                      |
| channel_id   | string | 子频道 ID                                 |
| channel_type | string | 子频道类型（2-音视频子频道 5-直播子频道） |
| guild_id     | string | 频道 ID                                   |
| user_id      | string | 用户 ID                                   |
| t            | string | 事件类型字段，如 GUILD_CREATE             |
| event_id     | sring  | 事件 ID                                   |

## Scope

- 作用域的枚举值

| 值      | 说明                   |
| ------- | ---------------------- |
| USER    | 代表只在当前用户有效   |
| GUILD   | 代表只在当前频道有效   |
| CHANNEL | 代表只在当前子频道有效 |
| GLOBAL  | 代表全局有效           |

## SessionStatus

- Session 状态的枚举值

| 值       | 说明                                                                |
| -------- | ------------------------------------------------------------------- |
| ACTIVE   | 此状态会检查并根据特定条件（gc timeout）自动删除 session            |
| INACTIVE | 此状态代表 session 正在运行中，会检查 timeout 并进入 INACTIVE 状态  |
| HANGING  | 此状态代表 session 不检查 timeout，但会在下次操作时进入 ACTIVE 状态 |

## SessionObject

- session 对象，用于存储 session 的数据

| 字段名   | 类型     | 说明                                                                                                 |
| -------- | -------- | ---------------------------------------------------------------------------------------------------- |
| scope    | Scope    | session 的作用域                                                                                     |
| status   | Status   | session 的状态                                                                                       |
| key      | Hashable | session 的键                                                                                         |
| data     | dict     | session 的值                                                                                         |
| identify | Hashable | scope 作用域下的标识，用户不输入时为消息数据自动填入的标识（如 Scope.USER 会为此项自动填入 user id） |

## CommandValidScenes

- 机器人命令的有效场景，用于限制机器人命令的有效场景，可传入多个场景，如 `CommandValidScenes.GUILD | CommandValidScenes.DM`
  - `GUILD` - 代表只在频道有效
  - `DM` - 代表只在频道私信有效
  - `GROUP` - 代表只在 qq 群聊场景有效
  - `C2C` - 代表只在 qq 私聊场景有效

## BotCommandObject

- 机器人的 on_command 命令对象，用于存储机器人命令的数据

| 字段名                  | 类型                           | 说明                                                                                             |
| ----------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------ |
| command                 | Iterable[str]                  | 可触发事件的指令列表，与正则 regex 互斥，优先使用此项                                            |
| regex                   | Iterable[Pattern]              | 可触发指令的正则 compile 实例或正则表达式，与指令表互斥                                          |
| func                    | Callable[[Model.MESSAGE], Any] | 指令触发后的回调函数                                                                             |
| treat                   | bool                           | 是否返回处理后的消息                                                                             |
| at                      | bool                           | 是否要求必须艾特机器人才能触发指令                                                               |
| short_circuit           | bool                           | 如果触发指令成功是否短路不运行后续指令（将根据注册顺序和 command 先 regex 后排序指令的短路机制） |
| is_custom_short_circuit | bool                           | 如果触发指令成功而回调函数返回 True 则不运行后续指令，存在时优先于 short_circuit                 |
| admin                   | bool                           | 是否要求频道主或或管理才可触发指令                                                               |
| admin_error_msg         | Optional[str]                  | 当 admin 为 True，而触发用户的权限不足时，如此项不为 None，返回此消息并短路；否则不进行短路      |

## AT

- 用于构建艾特其他用户的字符串

```python
from qg_botsdk import AT

AT('123456789')  ## 返回 "<@123456789>"
```
