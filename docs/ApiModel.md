# API Model

qg_botsdk 提供了 API Model 用于定义部分 API 的输入结构体

- 使用：

```python
from qg_botsdk import ApiModel
```

## BaseMessageApiModel

- SDK 内部使用的基础消息模型，其子类用于构建不同类型的消息对象

### Message（继承自 BaseMessageApiModel）

```python
ApiModel.Message()
```

- 构建一个普通消息对象，用于发送消息

| 参数                           |                                    |        |                                                                                                                                                                       |
| ------------------------------ | ---------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 字段名                         | 类型                               | 默认值 | 说明                                                                                                                                                                  |
| content                        | string None                        | None   | 消息内容文本或相应消息类型结构体（选填）                                                                                                                              |
| image                          | string None                        | None   | 图片 url，不可发送本地图片（选填）                                                                                                                                    |
| file_image                     | bytesBinaryIOstrPathLike[str] None | None   | 本地图片，可选以下三种方式传参：阅读档案后传入 bytes 类型图片数据、打开档案后直接传入档案、直接传入图片路径（具体例子可参阅 github example_10，要求 SDK 版本>=2.1.3） |
| message_id                     | string None                        | None   | 消息 id（选填，如此项数据项与 event_id 均为 None，则为此消息主动消息）                                                                                                |
| event_id                       | string None                        | None   | 事件 id（选填，如此项数据项与 message_id 均为 None，则为此消息主动消息）                                                                                              |
| message_reference_id           | string None                        | None   | 引用消息的 id（选填）                                                                                                                                                 |
| ignore_message_reference_error | bool None                          | None   | 是否忽略获取引用消息详情错误，默认否（选填）                                                                                                                          |

## MessageEmbed（继承自 BaseMessageApiModel）

```python
ApiModel.MessageEmbed()
```

- 构建一个 Embed 模板消息对象，用于发送消息

| 参数    |             |        |                                            |
| ------- | ----------- | ------ | ------------------------------------------ |
| 字段名  | 类型        | 默认值 | 说明                                       |
| title   | string None | None   | 消息标题（选填）                           |
| content | list None   | None   | 内容文本列表，每一项之间将存在分行（选填） |
| image   | string None | None   | 略缩图 url，不可发送本地图片（选填）       |
| prompt  | string None | None   | 消息弹窗通知的文本内容（选填）             |

## MessageArk23（继承自 BaseMessageApiModel）

```python
ApiModel.MessageArk23()
```

- 构建一个 Ark23 模板消息对象，用于发送消息

| 参数    |             |              |                                                                                                                   |
| ------- | ----------- | ------------ | ----------------------------------------------------------------------------------------------------------------- |
| 字段名  | 类型        | 默认值       | 说明                                                                                                              |
| content | list None   | 无，必选参数 | 内容文本列表，每一项之间将存在分行                                                                                |
| link    | list None   | 无，必选参数 | 链接 url 列表，长度应与内容列一致。将根据位置顺序填充文本超链接，如文本不希望填充链接可使用空文本或 None 填充位置 |
| desc    | string None | None         | 描述文本内容（选填）                                                                                              |
| prompt  | string None | None         | 消息弹窗通知的文本内容（选填）                                                                                    |

## MessageArk24（继承自 BaseMessageApiModel）

```python
ApiModel.MessageArk24()
```

- 构建一个 Ark24 模板消息对象，用于发送消息

| 参数      |             |        |                                      |
| --------- | ----------- | ------ | ------------------------------------ |
| 字段名    | 类型        | 默认值 | 说明                                 |
| title     | string None | None   | 消息标题（选填）                     |
| content   | string None | None   | 消息内容文本（选填）                 |
| subtitile | string None | None   | 消息标题（选填）                     |
| link      | string None | None   | 跳转的链接 url（选填）               |
| image     | string None | None   | 略缩图 url，不可发送本地图片（选填） |
| desc      | string None | None   | 描述文本内容（选填）                 |
| prompt    | string None | None   | 消息弹窗通知的文本内容（选填）       |

## MessageArk37（继承自 BaseMessageApiModel）

```python
ApiModel.MessageArk37()
```

- 构建一个 Ark37 模板消息对象，用于发送消息

| 参数    |             |        |                                      |
| ------- | ----------- | ------ | ------------------------------------ |
| 字段名  | 类型        | 默认值 | 说明                                 |
| title   | string None | None   | 消息标题（选填）                     |
| content | string None | None   | 消息内容文本（选填）                 |
| link    | string None | None   | 跳转的链接 url（选填）               |
| image   | string None | None   | 略缩图 url，不可发送本地图片（选填） |
| prompt  | string None | None   | 消息弹窗通知的文本内容（选填）       |

## MessageMarkdown（继承自 BaseMessageApiModel）

```python
ApiModel.MessageMarkdown()
```

- 构建一个 Markdown 模板消息对象，用于发送消息

| 参数             |                                  |        |                                                                                                          |
| ---------------- | -------------------------------- | ------ | -------------------------------------------------------------------------------------------------------- |
| 字段名           | 类型                             | 默认值 | 说明                                                                                                     |
| template_id      | string None                      | None   | markdown 模板 id（选填，与 content 不可同时存在）                                                        |
| key_values       | list\[{str: str/list[str]}] None | None   | markdown 模版 key values 列表，格式为：[{key1: value1}, {key2: value2}]（选填，与 content 不可同时存在） |
| content          | string None                      | None   | 原生 markdown 内容（选填，与 template_id, key, values 不可同时存在）                                     |
| keyboard_id      | string None                      | None   | keyboard 模板 id（选填，与 keyboard_content 不可同时存在）                                               |
| keyboard_content | dict None                        | None   | 原生 keyboard 内容（选填，与 keyboard_id 不可同时存在）                                                  |

> `template_id` `content` 至少需要有一个字段，否则无法下发消息
