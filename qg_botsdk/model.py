#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from enum import Enum
from re import Pattern
from re import compile as re_compile
from typing import (
    Any,
    BinaryIO,
    Callable,
    Dict,
    Hashable,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)

from ._api_model import BaseMessageApiModel, send_msg


class _AbstractEventClass(ABC):
    @abstractmethod
    def reply(
        self,
        content: Optional[Union[str, BaseMessageApiModel]] = None,
        image: Optional[str] = None,
        file_image: Optional[Union[bytes, BinaryIO, str]] = None,
        message_reference_id: Optional[str] = None,
        ignore_message_reference_error: Optional[bool] = None,
    ) -> send_msg():
        """
        直接回复相应事件的API，目前支持reply()发送被动消息的事件类型有:

        GUILD_MEMBER_ADD GUILD_MEMBER_UPDATE GUILD_MEMBER_REMOVE MESSAGE_REACTION_ADD MESSAGE_REACTION_REMOVE
        FORUM_THREAD_CREATE FORUM_THREAD_UPDATE FORUM_THREAD_DELETE FORUM_POST_CREATE FORUM_POST_DELETE
        FORUM_REPLY_CREATE FORUM_REPLY_DELETE INTERACTION_CREATE

        剩余事件的reply()将会转为发送主动消息

        :param content: 消息文本（选填，此项与image至少需要有一个字段，否则无法下发消息）
        :param image: 图片url，不可发送本地图片（选填，此项与msg至少需要有一个字段，否则无法下发消息）
        :param file_image: 本地图片，可选三种方式传参，具体可参阅github中的example_10或帮助文档
        :param message_reference_id: 引用消息的id（选填）
        :param ignore_message_reference_error: 是否忽略获取引用消息详情错误，默认否（选填）
        :return: 返回的.data中为解析后的json数据
        """
        ...


class _AbstractV2EventClass(ABC):
    @abstractmethod
    def reply(
        self,
        content: Optional[Union[str, BaseMessageApiModel]] = None,
        media_file_info: Optional[str] = None,
        message_reference_id: Optional[str] = None,
        ignore_message_reference_error: Optional[bool] = None,
        msg_seq: Optional[int] = None,
    ) -> send_msg():
        """
        直接回复相应事件的qq单聊、群事件 v2 API

        :param content: 消息体【或消息文本（选填，此项与image至少需要有一个字段，否则无法下发消息）】
        :param media_file_info: v2 qq相关接口使用，传入upload_media()获取的file_info字段
        :param message_reference_id: 引用消息的id（选填）
        :param ignore_message_reference_error: 是否忽略获取引用消息详情错误，默认否（选填）
        :param msg_seq: 直接替换ApiModel.Message内部构建递增的消息序号（选填）
        """
        ...


class Model:
    """
    使用此Model库可用作验证事件数据的准确性，目前可用的模型如下：

    GUILDS - 频道事件
    GUILD_MEMBERS -
    """

    class GUILDS(_AbstractEventClass, ABC):
        """
        频道事件的数据模型，可从t字段判断具体事件，其中包含：

        - GUILD_CREATE - 当机器人加入新guild时
        - GUILD_UPDATE - 当guild资料发生变更时
        - GUILD_DELETE - 当机器人退出guild时

        .. seealso::
            其子字段数据可参阅：
            https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#guilds
        """

        description: str
        icon: str
        id: str
        joined_at: str
        max_members: int
        member_count: int
        name: str
        op_user_id: str
        owner_id: str
        t: str
        event_id: str

    class CHANNELS(_AbstractEventClass, ABC):
        """
        子频道事件的数据模型，可从t字段判断具体事件，其中包含：

        - CHANNEL_CREATE - 当channel被创建时
        - CHANNEL_UPDATE - 当channel被更新时
        - CHANNEL_DELETE - 当channel被删除时

        .. seealso::
            其子字段数据可参阅：
            https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#channels-sdkv2-2-4
        """

        application_id: str
        guild_id: str
        id: str
        name: str
        op_user_id: str
        owner_id: str
        parent_id: str
        permissions: str
        position: int
        private_type: int
        speak_permission: int
        sub_type: int
        type: int
        t: str
        event_id: str

    class GUILD_MEMBERS(_AbstractEventClass, ABC):
        """
        频道成员事件的数据模型，可从t字段判断具体事件，其中包含：

        - GUILD_MEMBER_ADD - 当成员加入时
        - GUILD_MEMBER_UPDATE - 当成员资料变更时
        - GUILD_MEMBER_REMOVE - 当成员被移除时

        .. seealso::
             其子字段数据可参阅：
             https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#guild-members
        """

        class user:
            avatar: str
            bot: bool
            id: str
            username: str

        guild_id: str
        joined_at: str
        nick: str
        op_user_id: str
        roles: List[str]
        t: str
        event_id: str

    class MESSAGE(_AbstractEventClass, ABC):
        """
        消息事件的数据模，可从t字段判断具体事件，其中包含：

        - MESSAGE_CREATE - 发送消息事件，代表频道内的全部消息，而不只是 at 机器人的消息
        - AT_MESSAGE_CREATE - 当收到@机器人的消息时

        .. note::
            私域机器人可接收全部消息事件、公域机器人仅能接收艾特机器人的消息事件

        .. seealso::
             其子字段数据可参阅：
             https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#message
        """

        class __MsgMentions:
            avatar: str
            bot: bool
            id: str
            username: str

        class __MsgAttachments:
            content_type: str
            filename: str
            height: int
            width: int
            id: str
            size: int
            url: str

        class message_reference:
            message_id: str

        class author:
            avatar: str
            bot: bool
            id: str
            username: str

        class member:
            joined_at: str
            nick: str
            roles: List[str]

        channel_id: str
        guild_id: str
        content: str
        id: str
        mentions = List[__MsgMentions]
        attachments = List[__MsgAttachments]
        seq: int
        seq_in_channel: str
        timestamp: str
        tts: bool
        pinned: bool
        type: int
        flags: int
        treated_msg: Union[str, Tuple]
        t: str
        event_id: str

    class MESSAGE_DELETE(_AbstractEventClass, ABC):
        """
        消息撤回事件的数据模型，可从t字段判断具体事件，其中包含：

        - MESSAGE_DELETE - 删除（撤回）消息事件
        - PUBLIC_MESSAGE_DELETE - 当频道的消息被删除时
        - DIRECT_MESSAGE_DELETE - 删除（撤回）私信消息事件

        .. note::
            私域机器人可接收MESSAGE_DELETE、公域机器人仅能接收PUBLIC_MESSAGE_DELETE

        .. seealso::
             其子字段数据可参阅：
             https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#message-delete
        """

        class message:
            class author:
                bot: bool
                id: str
                username: str

            channel_id: str
            guild_id: str
            id: str

        class op_user:
            id: str

        t: str
        event_id: str

    class DIRECT_MESSAGE(_AbstractEventClass, ABC):
        """
        私信消息事件的数据模型，可从t字段判断具体事件，其中包含：

        - DIRECT_MESSAGE_CREATE - 当收到用户发给机器人的私信消息时

        .. seealso::
             其子字段数据可参阅：
             https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#direct-message
        """

        class __MsgAttachments:
            content_type: str
            filename: str
            height: int
            width: int
            id: str
            size: int
            url: str

        class message_reference:
            message_id: str

        class author:
            avatar: str
            id: str
            username: str

        class member:
            joined_at: str

        channel_id: str
        guild_id: str
        content: str
        direct_message: bool
        id: str
        attachments = List[__MsgAttachments]
        seq: int
        seq_in_channel: str
        src_guild_id: str
        timestamp: str
        treated_msg: str
        t: str
        event_id: str

    class MESSAGE_AUDIT(_AbstractEventClass, ABC):
        """
        主动消息审核事件的数据模型，可从t字段判断具体事件，其中包含：

        - MESSAGE_AUDIT_PASS - 消息审核通过
        - MESSAGE_AUDIT_REJECT - 消息审核不通过

        .. note::
            注意，只有审核通过事件（MESSAGE_AUDIT_PASS）才会有message_id的值

        .. seealso::
             其子字段数据可参阅：
             https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#message-audit
        """

        audit_id: str
        audit_time: str
        create_time: str
        channel_id: str
        guild_id: str
        message_id: str
        t: str
        event_id: str

    class FORUMS_EVENT(_AbstractEventClass, ABC):
        """
        论坛事件的数据模型，可从t字段判断具体事件，其中包含：

        - FORUM_THREAD_CREATE - 当用户创建主题（帖子）时
        - FORUM_THREAD_UPDATE - 当用户更新主题（帖子）时
        - FORUM_THREAD_DELETE - 当用户删除主题（帖子）时

        *剩余论坛事件（如回帖和回复回帖）暂未有相关推送*

        .. note::
            现有推送的type字段：

            - type 1 - 普通文本，子字段text
            - type 4 - url信息，子字段url

            现无推送，根据文档列出的type：

            - 原新type 2 - 图片，子字段image（曾短暂出现，目前为空子字段，无任何内容反馈）
            - 原新type 3 - 视频，子字段video（曾短暂出现，目前为空子字段，无任何内容反馈）
            - 原type 2 - at信息，目前为空子字段，无任何内容反馈
            - 原type 4 - 表情，目前为空子字段，无任何内容反馈
            - 原type 5 - #子频道，目前为空子字段，无任何内容反馈

        .. seealso::
             其子字段数据可参阅：
             https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#forums-event
        """

        class thread_info:
            class title:
                class __ForumsTitle:
                    class __ForumsSubTitle:
                        class text:
                            text: str

                        type: int

                    elems: List[__ForumsSubTitle]
                    props: object

                paragraphs: List[__ForumsTitle]

            class content:
                class __ForumsContent:
                    class __ForumsSubContent:
                        class text:  # type = 1
                            text: str

                        #                         class image:  # type = 2
                        #                             class plat_image:
                        #                                 url: str
                        #                                 width: int
                        #                                 height: int
                        #                                 image_id: str
                        #
                        #                         class video:  # type = 3
                        #                             class plat_video:
                        #                                 class cover:
                        #                                     url: str
                        #                                     width: int
                        #                                     height: int
                        #
                        #                                 url: str
                        #                                 width: int
                        #                                 height: int
                        #                                 video_id: str

                        class url:  # type = 4
                            url: str
                            desc: str

                        type = int

                    elems: List[__ForumsSubContent]
                    props: object

                paragraphs: List[__ForumsContent]

            thread_id: str
            date_time: str

        guild_id: str
        channel_id: str
        author_id: str
        t: str
        event_id: str

    class OPEN_FORUMS(_AbstractEventClass, ABC):
        """
        公域论坛事件的数据模型，可从t字段判断具体事件，其中包含：

        - OPEN_FORUM_THREAD_CREATE - 当用户创建主题（帖子）时
        - OPEN_FORUM_THREAD_UPDATE - 当用户更新主题（帖子）时
        - OPEN_FORUM_THREAD_DELETE - 当用户删除主题（帖子）时

        *剩余公域论坛事件（如回帖和回复回帖）暂未有相关推送*

        .. seealso::
             其子字段数据可参阅：
             https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#open-forums
        """

        guild_id: str
        channel_id: str
        author_id: str
        t: str
        event_id: str

    class AUDIO_ACTION(_AbstractEventClass, ABC):
        """
        音频事件的数据模型，可从t字段判断具体事件，其中包含：

        - AUDIO_START - 音频开始播放时
        - AUDIO_FINISH - 音频播放结束时
        - AUDIO_ON_MIC - 上麦时
        - AUDIO_OFF_MIC - 下麦时

        .. note::
            注意，只有AUDIO_START、AUDIO_FINISH拥有audio_url和text字段

        .. seealso::
             其子字段数据可参阅：
             https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#audio-action
        """

        channel_id: str
        guild_id: str
        audio_url: str
        text: str
        t: str
        event_id: str

    class REACTION(_AbstractEventClass, ABC):
        """
        表情表态事件的数据模型，可从t字段判断具体事件，其中包含：

        - MESSAGE_REACTION_ADD - 为消息添加表情表态
        - MESSAGE_REACTION_REMOVE - 为消息删除表情表态

        .. seealso::
             其子字段数据可参阅：
             https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#reaction
        """

        class emoji:
            id: str
            type: int

        class target:
            id: str
            type: int

        user_id: str
        channel_id: str
        guild_id: str
        t: str
        event_id: str

    class INTERACTION(_AbstractEventClass, ABC):
        """
        互动事件的数据模型，可从t字段判断具体事件，其中包含：

        - INTERACTION_CREATE - 互动事件创建时

        .. seealso::
             其子字段数据可参阅：
             https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#interaction
        """

        class data:
            class resolved:
                button_data: str
                button_id: str
                message_id: str
                user_id: str

            type: int

        t: str
        event_id: str
        id: str
        type: int
        chat_type: int
        guild_id: str
        channel_id: str
        group_open_id: str
        version: int
        application_id: str

    class LIVE_CHANNEL_MEMBER(_AbstractEventClass, ABC):
        """
        音视频/直播子频道成员进出事件的数据模型，可从t字段判断具体事件，其中包含：

        - AUDIO_OR_LIVE_CHANNEL_MEMBER_ENTER - 当用户进入音视频/直播子频道
        - AUDIO_OR_LIVE_CHANNEL_MEMBER_EXIT - 当用户离开音视频/直播子频道

        .. seealso::
             其子字段数据可参阅：
             https://qg-botsdk.readthedocs.io/zh_CN/latest/Model%E5%BA%93.html#live_channel_member
        """

        channel_id: str
        channel_type: int
        guild_id: str
        user_id: str
        t: str
        event_id: str

    class GROUP_EVENTS(_AbstractV2EventClass, ABC):
        """
        群聊机器人加入/退出群聊以及群聊拒绝/接受机器人主动消息的事件模型, 可从t字段判断具体事件, 其中包含:
        - GROUP_ADD_ROBOT  - 机器人加入群聊
        - GROUP_DEL_ROBOT  - 机器人退出群聊
        - GROUP_MSG_REJECT - 群聊拒绝机器人主动消息
        - GROUP_MSG_RECEIVE - 群聊接受机器人主动消息

        .. seealso::
             其子字段数据可参阅：
             https://bot.q.qq.com/wiki/develop/api-v2/server-inter/group/manage/event.html
        """

        t: str
        id: str
        group_openid: str
        op_member_openid: str
        timestamp: str

    class FRIEND_EVENTS(_AbstractV2EventClass, ABC):
        """
        用户添加/删除机器人以及用户拒绝/接受机器人主动消息的事件模型, 可从t字段判断具体事件, 其中包含:
        - FRIEND_ADD - 用户添加机器人
        - FRIEND_DEL - 用户删除机器人
        - C2C_MSG_REJECT - 用户拒绝机器人主动消息
        - C2C_MSG_RECEIVE - 用户接受机器人主动消息

        .. seealso::
             其子字段数据可参阅：
             https://bot.q.qq.com/wiki/develop/api-v2/server-inter/user/manage/event.html
        """

        t: str
        id: str
        openid: str
        timestamp: str

    class GROUP_MESSAGE(_AbstractV2EventClass, ABC):
        """
        用户在群内@机器人发动的消息的事件模型, 可从t字段判断具体事件, 其中包含:
        - GROUP_AT_MESSAGE_CREATE - 用户在群聊@机器人发送消息

        .. seealso::
             其子字段数据可参阅：
             https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/send-receive/event.html#%E7%BE%A4%E8%81%8A-%E6%9C%BA%E5%99%A8%E4%BA%BA
        """

        class __MsgAttachments:
            content_type: str
            filename: str
            height: int
            width: int
            size: int
            url: str

        class author:
            member_openid: str

        id: str
        group_openid: str
        content: str
        attachments = List[__MsgAttachments]
        timestamp: str
        treated_msg: Union[str, Tuple]

    class C2C_MESSAGE(_AbstractV2EventClass, ABC):
        """
        用户在单聊发送消息给机器人的事件模型, 可从t字段判断具体事件, 其中包含:
        - C2C_MESSAGE_CREATE - 用户在群聊@机器人发送消息

        .. seealso::
             其子字段数据可参阅：
             https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/send-receive/event.html#%E5%8D%95%E8%81%8A%E6%B6%88%E6%81%AF
        """

        class __MsgAttachments:
            content_type: str
            filename: str
            height: int
            width: int
            size: int
            url: str

        class author:
            user_openid: str

        id: str
        content: str
        attachments = List[__MsgAttachments]
        timestamp: str
        treated_msg: Union[str, Tuple]


class Scope(Enum):
    USER = "USER"  # 代表只在当前用户有效
    GUILD = "GUILD"  # 代表只在当前频道有效
    CHANNEL = "CHANNEL"  # 代表只在当前子频道有效
    GROUP = "GROUP"  # 代表只在当前qq群聊有效
    GLOBAL = "GLOBAL"  # 代表在全局有效


class SessionStatus(Enum):
    INACTIVE = 0  # 此状态会检查并根据特定条件（gc timeout）自动删除session
    ACTIVE = 1  # 此状态代表session正在运行中，会检查timeout并进入INACTIVE状态
    HANGING = 2  # 此状态代表session不检查timeout，但会在下次操作时进入ACTIVE状态


class SessionObject:
    """
    session对象，用于存储session的数据

    :param scope: session的作用域
    :param status: session的状态
    :param key: session的键
    :param data: session的值
    :param identify: scope作用域下的标识，不输入时为消息数据自动填入的标识（如Scope.USER会为此项自动填入user id）
    """

    def __init__(
        self,
        scope: Scope,
        status: SessionStatus,
        key: Hashable,
        data: Dict,
        identify: Hashable = None,
    ):
        self.scope: Scope = scope
        self.status: SessionStatus = status
        self.key: Hashable = key
        self.data: Dict = data
        self.identify: Hashable = identify

    def __repr__(self):
        return (
            f"<SessionObject scope={self.scope} status={self.status} key={self.key} "
            f"data={self.data} identify={self.identify}>"
        )


class CommandValidScenes(int):
    """
    机器人命令的有效场景，用于限制机器人命令的有效场景，可传入多个场景，如 CommandValidScenes.GUILD | CommandValidScenes.DM

    - GUILD - 代表只在频道有效
    - DM - 代表只在频道私信有效
    - GROUP - 代表只在qq群聊场景有效
    - C2C - 代表只在qq私聊场景有效
    """

    GUILD = 1
    DM = 2
    GROUP = 4
    C2C = 8
    ALL = GUILD | DM | GROUP | C2C


class BotCommandObject:
    """
    机器人的on_command命令对象，用于存储机器人命令的数据

    :param command: 可触发事件的指令列表，与正则 regex 互斥，优先使用此项
    :param regex: 可触发指令的正则 compile 实例或正则表达式，与指令表互斥
    :param func: 指令触发后的回调函数
    :param treat: 是否返回处理后的消息
    :param at: 是否要求必须艾特机器人才能触发指令
    :param short_circuit: 如果触发指令成功是否短路不运行后续指令（将根据注册顺序和 command 先 regex 后排序指令的短路机制）
    :param is_custom_short_circuit: 如果触发指令成功而回调函数返回True则不运行后续指令，存在时优先于short_circuit
    :param admin: 是否要求频道主或或管理才可触发指令
    :param admin_error_msg: 当admin为True，而触发用户的权限不足时，如此项不为None，返回此消息并短路；否则不进行短路
    :param valid_scenes: 此机器人命令的有效场景，可传入多个场景，如 CommandValidScenes.GUILD|CommandValidScenes.DM，默认全部
    """

    def __init__(
        self,
        command: Iterable[str] = None,
        regex: Iterable[Pattern] = None,
        func: Callable[
            [Union[Model.MESSAGE, Model.GROUP_MESSAGE, Model.C2C_MESSAGE]], Any
        ] = None,
        treat: bool = True,
        at: bool = False,
        short_circuit: bool = True,
        is_custom_short_circuit: bool = False,
        admin: bool = False,
        admin_error_msg: Optional[str] = None,
        valid_scenes: CommandValidScenes = CommandValidScenes.ALL,
    ):
        # type checking for user input, not included items are not important(for wait_for api)
        if command is not None:
            if isinstance(command, str):
                command = (command,)
            elif isinstance(command, Iterable):
                for i in command:
                    if not isinstance(i, str):
                        raise TypeError("command must be of type Iterable[str]")
            else:
                raise TypeError("command must be of type Iterable[str]")
        _regex = None
        if regex is not None:
            if isinstance(regex, Pattern):
                _regex = (regex,)
            elif isinstance(regex, str):
                _regex = (re_compile(regex),)
            elif isinstance(regex, Iterable):
                _regex = []
                for x in regex:
                    if isinstance(x, str):
                        _regex.append(re_compile(x))
                    elif isinstance(x, Pattern):
                        _regex.append(x)
                    else:
                        raise TypeError("regex must be of type Iterable[Pattern]")
            else:
                raise TypeError("regex must be of type Iterable[Pattern]")
        if not isinstance(treat, bool):
            raise TypeError("treat must be of type bool")
        if not isinstance(at, bool):
            raise TypeError("at must be of type bool")
        if not isinstance(short_circuit, bool):
            raise TypeError("short_circuit must be of type bool")
        # init
        self.command: Iterable[str] = command
        self.regex: Iterable[Pattern] = _regex
        self.func: Callable[
            [Union[Model.MESSAGE, Model.GROUP_MESSAGE, Model.C2C_MESSAGE]], Any
        ] = func
        self.treat: bool = treat
        self.at: bool = at
        self.short_circuit: bool = short_circuit
        self.is_custom_short_circuit: bool = is_custom_short_circuit
        self.admin: bool = admin
        self.admin_error_msg: Optional[str] = admin_error_msg
        self.valid_scenes: CommandValidScenes = valid_scenes

    def __repr__(self):
        if self.command:
            return f"<BotCommandObject command={self.command} func={self.func} valid_scenes={self.valid_scenes}>"
        else:
            return f"<BotCommandObject regex={self.regex} func={self.func} valid_scenes={self.valid_scenes}>"


class AnnounceRecommendChannels:
    def __init__(self, channel_id: str, introduce: str):
        self.channel_id = channel_id
        self.introduce = introduce

    def __json__(self):
        return {"channel_id": self.channel_id, "introduce": self.introduce}


class AT(str):
    def __new__(cls, user_id: str):
        """
        用于构建艾特其他用户的字符串

        :param user_id: 要@的用户id
        """
        return super().__new__(cls, f"<@{user_id}>")


class EmojiID:
    得意 = 4
    流泪 = 5
    睡 = 8
    大哭 = 9
    尴尬 = 10
    调皮 = 12
    微笑 = 14
    酷 = 16
    可爱 = 21
    傲慢 = 23
    饥饿 = 24
    困 = 25
    惊恐 = 26
    流汗 = 27
    憨笑 = 28
    悠闲 = 29
    奋斗 = 30
    疑问 = 32
    嘘 = 33
    晕 = 34
    敲打 = 38
    再见 = 39
    发抖 = 41
    爱情 = 42
    跳跳 = 43
    拥抱 = 49
    蛋糕 = 53
    咖啡 = 60
    玫瑰 = 63
    爱心 = 66
    太阳 = 74
    月亮 = 75
    赞 = 76
    握手 = 78
    胜利 = 79
    飞吻 = 85
    西瓜 = 89
    冷汗 = 96
    擦汗 = 97
    抠鼻 = 98
    鼓掌 = 99
    糗大了 = 100
    坏笑 = 101
    左哼哼 = 102
    右哼哼 = 103
    哈欠 = 104
    委屈 = 106
    左亲亲 = 109
    可怜 = 111
    示爱 = 116
    抱拳 = 118
    拳头 = 120
    爱你 = 122
    NO = 123
    OK = 124
    转圈 = 125
    挥手 = 129
    喝彩 = 144
    棒棒糖 = 147
    茶 = 171
    泪奔 = 173
    无奈 = 174
    卖萌 = 175
    小纠结 = 176
    doge = 179
    惊喜 = 180
    骚扰 = 181
    笑哭 = 182
    我最美 = 183
    点赞 = 201
    托脸 = 203
    托腮 = 212
    啵啵 = 214
    蹭一蹭 = 219
    抱抱 = 222
    拍手 = 227
    佛系 = 232
    喷脸 = 240
    甩头 = 243
    加油抱抱 = 246
    脑阔疼 = 262
    捂脸 = 264
    辣眼睛 = 265
    哦哟 = 266
    头秃 = 267
    问号脸 = 268
    暗中观察 = 269
    emm = 270
    吃瓜 = 271
    呵呵哒 = 272
    我酸了 = 273
    汪汪 = 277
    汗 = 278
    无眼笑 = 281
    敬礼 = 282
    面无表情 = 284
    摸鱼 = 285
    哦 = 287
    睁眼 = 289
    敲开心 = 290
    摸锦鲤 = 293
    期待 = 294
    拜谢 = 297
    元宝 = 298
    牛啊 = 299
    右亲亲 = 305
    牛气冲天 = 306
    喵喵 = 307
    仔细分析 = 314
    加油 = 315
    崇拜 = 318
    比心 = 319
    庆祝 = 320
    拒绝 = 322
    吃糖 = 324
    生气 = 326


class EmojiString:
    得意 = "<emoji:4>"
    流泪 = "<emoji:5>"
    睡 = "<emoji:8>"
    大哭 = "<emoji:9>"
    尴尬 = "<emoji:10>"
    调皮 = "<emoji:12>"
    微笑 = "<emoji:14>"
    酷 = "<emoji:16>"
    可爱 = "<emoji:21>"
    傲慢 = "<emoji:23>"
    饥饿 = "<emoji:24>"
    困 = "<emoji:25>"
    惊恐 = "<emoji:26>"
    流汗 = "<emoji:27>"
    憨笑 = "<emoji:28>"
    悠闲 = "<emoji:29>"
    奋斗 = "<emoji:30>"
    疑问 = "<emoji:32>"
    嘘 = "<emoji:33>"
    晕 = "<emoji:34>"
    敲打 = "<emoji:38>"
    再见 = "<emoji:39>"
    发抖 = "<emoji:41>"
    爱情 = "<emoji:42>"
    跳跳 = "<emoji:43>"
    拥抱 = "<emoji:49>"
    蛋糕 = "<emoji:53>"
    咖啡 = "<emoji:60>"
    玫瑰 = "<emoji:63>"
    爱心 = "<emoji:66>"
    太阳 = "<emoji:74>"
    月亮 = "<emoji:75>"
    赞 = "<emoji:76>"
    握手 = "<emoji:78>"
    胜利 = "<emoji:79>"
    飞吻 = "<emoji:85>"
    西瓜 = "<emoji:89>"
    冷汗 = "<emoji:96>"
    擦汗 = "<emoji:97>"
    抠鼻 = "<emoji:98>"
    鼓掌 = "<emoji:99>"
    糗大了 = "<emoji:100>"
    坏笑 = "<emoji:101>"
    左哼哼 = "<emoji:102>"
    右哼哼 = "<emoji:103>"
    哈欠 = "<emoji:104>"
    委屈 = "<emoji:106>"
    左亲亲 = "<emoji:109>"
    可怜 = "<emoji:111>"
    示爱 = "<emoji:116>"
    抱拳 = "<emoji:118>"
    拳头 = "<emoji:120>"
    爱你 = "<emoji:122>"
    NO = "<emoji:123>"
    OK = "<emoji:124>"
    转圈 = "<emoji:125>"
    挥手 = "<emoji:129>"
    喝彩 = "<emoji:144>"
    棒棒糖 = "<emoji:147>"
    茶 = "<emoji:171>"
    泪奔 = "<emoji:173>"
    无奈 = "<emoji:174>"
    卖萌 = "<emoji:175>"
    小纠结 = "<emoji:176>"
    doge = "<emoji:179>"
    惊喜 = "<emoji:180>"
    骚扰 = "<emoji:181>"
    笑哭 = "<emoji:182>"
    我最美 = "<emoji:183>"
    点赞 = "<emoji:201>"
    托脸 = "<emoji:203>"
    托腮 = "<emoji:212>"
    啵啵 = "<emoji:214>"
    蹭一蹭 = "<emoji:219>"
    抱抱 = "<emoji:222>"
    拍手 = "<emoji:227>"
    佛系 = "<emoji:232>"
    喷脸 = "<emoji:240>"
    甩头 = "<emoji:243>"
    加油抱抱 = "<emoji:246>"
    脑阔疼 = "<emoji:262>"
    捂脸 = "<emoji:264>"
    辣眼睛 = "<emoji:265>"
    哦哟 = "<emoji:266>"
    头秃 = "<emoji:267>"
    问号脸 = "<emoji:268>"
    暗中观察 = "<emoji:269>"
    emm = "<emoji:270>"
    吃瓜 = "<emoji:271>"
    呵呵哒 = "<emoji:272>"
    我酸了 = "<emoji:273>"
    汪汪 = "<emoji:277>"
    汗 = "<emoji:278>"
    无眼笑 = "<emoji:281>"
    敬礼 = "<emoji:282>"
    面无表情 = "<emoji:284>"
    摸鱼 = "<emoji:285>"
    哦 = "<emoji:287>"
    睁眼 = "<emoji:289>"
    敲开心 = "<emoji:290>"
    摸锦鲤 = "<emoji:293>"
    期待 = "<emoji:294>"
    拜谢 = "<emoji:297>"
    元宝 = "<emoji:298>"
    牛啊 = "<emoji:299>"
    右亲亲 = "<emoji:305>"
    牛气冲天 = "<emoji:306>"
    喵喵 = "<emoji:307>"
    仔细分析 = "<emoji:314>"
    加油 = "<emoji:315>"
    崇拜 = "<emoji:318>"
    比心 = "<emoji:319>"
    庆祝 = "<emoji:320>"
    拒绝 = "<emoji:322>"
    吃糖 = "<emoji:324>"
    生气 = "<emoji:326>"


class WaifForCommandCallback:
    def __init__(
        self, command: BotCommandObject, callback: Callable[[Model.MESSAGE], Any]
    ):
        self.command = command
        self.callback = callback
