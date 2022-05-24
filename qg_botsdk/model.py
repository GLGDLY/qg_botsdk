# !/usr/bin/env python3
# encoding: utf-8
class Model:
    def __init__(self):
        self._MsgMentions: object

    class GUILDS:
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

    class GUILD_MEMBERS:
        class user:
            avatar: str
            bot: bool
            id: str
            username: str

        guild_id: str
        joined_at: str
        nick: str
        op_user_id: str
        roles: list[str]
        t: str
        event_id: str

    class MESSAGE:
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
            roles: list[str]

        channel_id: str
        guild_id: str
        content: str
        id: str
        mentions = [__MsgMentions]
        attachments = [__MsgAttachments]
        seq: int
        seq_in_channel: str
        timestamp: str
        treated_msg: str
        t: str
        event_id: str

    class MESSAGE_DELETE:
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

    class DIRECT_MESSAGE:
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
            roles: list[str]

        channel_id: str
        guild_id: str
        content: str
        id: str
        attachments = [__MsgAttachments]
        seq: int
        seq_in_channel: str
        src_guild_id: str
        timestamp: str
        treated_msg: str
        t: str
        event_id: str

    class MESSAGE_AUDIT:
        """
        只有审核通过事件才会有message_id的值
        """
        audit_id: str
        audit_time: str
        create_time: str
        channel_id: str
        guild_id: str
        message_id: str
        t: str
        event_id: str

    class FORUMS_EVENT:
        """
        现有推送的type字段：
        type 1：普通文本，子字段text
        type 2：图片，子字段image
        type 3：视频，子字段video
        type 4：url信息，子字段url

        现无推送，根据文档列出的type：
        原type 2：at信息，目前为空子字段，无任何内容反馈
        原type 4：表情，目前为空子字段，无任何内容反馈
        原type 5：#子频道，目前为空子字段，无任何内容反馈
        """

        class thread_info:
            class title:
                class __ForumsTitle:
                    class __ForumsSubTitle:
                        class text:
                            text: str

                        type: int

                    elems: list[__ForumsSubTitle]
                    props: object

                paragraphs: list[__ForumsTitle]

            class content:
                class __ForumsContent:
                    class __ForumsSubContent:
                        class text:  # type = 1
                            text: str

                        class image:  # type = 2
                            class plat_image:
                                url: str
                                width: int
                                height: int
                                image_id: str

                        class video:  # type = 3
                            class plat_video:
                                class cover:
                                    url: str
                                    width: int
                                    height: int

                                url: str
                                width: int
                                height: int
                                video_id: str

                        class url:  # type = 4
                            url: str
                            desc: str

                        type = int

                    elems: list[__ForumsSubContent]
                    props: object

                paragraphs: list[__ForumsContent]

            thread_id: str
            date_time: str

        guild_id: str
        channel_id: str
        author_id: str
        t: str
        event_id: str

    class AUDIO_ACTION:
        """
        只有AUDIO_START、AUDIO_FINISH拥有audio_url和text字段
        """
        channel_id: str
        guild_id: str
        audio_url: str
        text: str
        t: str
        event_id: str

    class REACTION:
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
