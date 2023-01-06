# Plugins 插件开发

qg_botsdk提供了支援完全seperate programming的插件开发模式，并提供了相应的各种参数方便不同场景下使用。

## 开发

```python
from qg_botsdk import Plugins   ## 导入插件开发模块
```

导入后，即可开始开发本插件的不同子项。Plugins插件的模块其实与BOT装饰器基本相通，只不过Plugins提供了无需关联主程序的一种编程方式，开发完成后主程序直接import导入即可使用里面注册的消息处理器。

### 预处理器

预处理器会在进入任何消息处理器、检查所有commands前运行，常用于编写log相关的模块。

```python
@Plugins.before_command()
def preprocessor(data: Model.Message):
    print(f"收到了消息：{data.treated_msg}")
```

> 无参数

### 注册消息指令

注册plugins指令装饰器，可用于分割式编写指令并注册进机器人注册plugins指令装饰器，可用于分割式编写指令并注册进机器人

```python
@Plugins.on_command("p_0", is_short_circuit=True)
def p_0(data: Model.MESSAGE):
    data.reply("使用plugins的on_command模块进行注册，用户消息包含指令p_0可触发此函数")
```

| 参数                      |                                |       |                                                               |
| ----------------------- | ------------------------------ | ----- | ------------------------------------------------------------- |
| 字段名                     | 类型                             | 默认值   | 说明                                                            |
| command                 | List[string], string           | None  | 可触发事件的指令列表，与正则regex互斥，优先使用此项                                  |
| regex                   | regex compiled Pattern, string | None  | 可触发指令的正则compile实例或正则表达式，与指令表互斥                                |
| is_treat                | bool                           | True  | 是否在treated_msg中同时处理指令，如正则将返回.groups()                         |
| is_require_at           | bool                           | False | 是否要求必须艾特机器人才能触发指令                                             |
| is_short_circuit        | bool                           | True  | 如果触发指令成功是否短路不运行后续指令（将根据注册顺序排序指令的短路机制）                         |
| is_custom_short_circuit | bool                           | False | 如果触发指令成功而返回True则不运行后续指令，与is_short_circuit不能同时存在               |
| is_require_admin        | bool                           | False | 是否要求频道主或或管理才可触发指令，默认否                                         |
| admin_error_msg         | string                         | None  | 当is_require_admin为True，而触发用户的权限不足时，如此项不为None，返回此消息并短路；否则不进行短路 |

## 使用

> 假设Plugins编写的文件为my_plugins.py

### 方法1：直接import

> 使用plugins的方法一，直接import相应module，BOT.start()时将自动加载使用plugins的方法一，直接import相应module，BOT.start()时将自动加载

```python
import my_plugins
```

### [推荐]方法2：使用BOT.load_plugins()

> 使用plugins的方法二，使用BOT.load_plugins()加载使用plugins的方法二，使用BOT.load_plugins()加载

```python
BOT.load_plugins("my_plugins.py")
```

## 实际用例

可查看github中的example库的example13：

<https://github.com/GLGDLY/qg_botsdk/blob/master/example/example_13(%E8%A3%85%E9%A5%B0%E5%99%A8).py>
<https://github.com/GLGDLY/qg_botsdk/blob/master/example/example_13_plugins.py>
