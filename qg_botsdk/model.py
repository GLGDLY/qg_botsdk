__all__ = ['GUILDS', 'GUILD_MEMBERS', 'MESSAGE', 'MESSAGE_DELETE', 'DIRECT_MESSAGE', 'MESSAGE_AUDIT',
           'FORUMS_EVENT', 'AUDIO_ACTION', 'REACTION']


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


class MsgAttachments:
    content_type: str
    filename: str
    height: int
    width: int
    id: str
    size: int
    url: str


class MsgMentions:
    avatar: str
    bot: bool
    id: str
    username: str


class MsgReference:
    message_id: str


class MESSAGE:
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
    mentions = [MsgMentions]
    attachments = [MsgAttachments]
    message_reference = MsgReference
    seq: int
    seq_in_channel: str
    timestamp: str
    treated_msg: str
    t: str


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


class DIRECT_MESSAGE:
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
    attachments = [MsgAttachments]
    message_reference = MsgReference
    seq: int
    seq_in_channel: str
    src_guild_id: str
    timestamp: str
    treated_msg: str
    t: str


class MESSAGE_AUDIT:
    """
    只有审核通过事件才会有message_id的值
    """
    audit_id: str
    audit_time: str
    channel_id: str
    create_time: str
    guild_id: str
    message_id: str
    t: str


class ForumsSubTitle:
    class text:
        text: str
    type: int


class ForumsTitle:
    elems: list[ForumsSubTitle]
    props: object


class ForumsSubContent:
    class text:
        text: str

    class url:
        url: str
        desc: str

    type = int


class ForumsContent:
    elems: list[ForumsSubContent]
    props: object


class FORUMS_EVENT:
    """
    现有信息的type字段：
    type 1：普通文本，子字段text
    type 4：url信息，子字段url

    现无消息，根据文档列出的type：
    原type 2：at信息，目前为空子字段，无任何内容反馈
    原type 4：表情，目前为空子字段，无任何内容反馈
    原type 5：#子频道，目前为空子字段，无任何内容反馈
    原type 10：视频，目前为空子字段，无任何内容反馈
    原type 11：图片，目前为空子字段，无任何内容反馈
    """
    class thread_info:
        class title:
            paragraphs: list[ForumsTitle]

        class content:
            paragraphs: list[ForumsContent]

        thread_id: str
    guild_id: str
    channel_id: str
    author_id: str
    date_time: str
    thread_id: str
    post_id: str
    t: str


class AUDIO_ACTION:
    """
    只有AUDIO_START、AUDIO_FINISH拥有audio_url和text字段
    """
    channel_id: str
    guild_id: str
    audio_url: str
    text: str


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

