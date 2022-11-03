# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Union

from ._utils import event_class


class Model:
    """
    使用此Model库可用作验证事件数据的准确性，目前可用的模型如下：

    GUILDS - 频道事件
    GUILD_MEMBERS -
    """

    class GUILDS(event_class):
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

    class CHANNELS(event_class):
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

    class GUILD_MEMBERS(event_class):
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

    class MESSAGE(event_class):
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
        treated_msg: Union[str, tuple]
        t: str
        event_id: str

    class MESSAGE_DELETE(event_class):
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

    class DIRECT_MESSAGE(event_class):
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

    class MESSAGE_AUDIT(event_class):
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

    class FORUMS_EVENT(event_class):
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

    class OPEN_FORUMS(event_class):
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

    class AUDIO_ACTION(event_class):
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

    class REACTION(event_class):
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

    class INTERACTION(event_class):
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

        application_id: str
        channel_id: str
        guild_id: str
        id: str
        type: int
        version: int
        t: str
        event_id: str

    class LIVE_CHANNEL_MEMBER(event_class):
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
