from ._statics import EVENTS, EVENTS_ENUM
from .model import Model

EVENTS_TO_DISPATCH = {
    **dict(
        zip(
            EVENTS.GUILD,
            [("on_guild_event", EVENTS_ENUM.GUILD)] * len(EVENTS.GUILD),
        )
    ),
    **dict(
        zip(
            EVENTS.CHANNEL,
            [("on_channel_event", EVENTS_ENUM.CHANNEL)] * len(EVENTS.CHANNEL),
        )
    ),
    **dict(
        zip(
            EVENTS.GUILD_MEMBER,
            [("on_guild_member", EVENTS_ENUM.GUILD_MEMBER)] * len(EVENTS.GUILD_MEMBER),
        )
    ),
    **dict(
        zip(
            EVENTS.REACTION,
            [("on_reaction", EVENTS_ENUM.REACTION)] * len(EVENTS.REACTION),
        )
    ),
    **dict(
        zip(
            EVENTS.INTERACTION,
            [("on_interaction", EVENTS_ENUM.INTERACTION)] * len(EVENTS.INTERACTION),
        )
    ),
    **dict(zip(EVENTS.AUDIT, [("on_audit", EVENTS_ENUM.AUDIT)] * len(EVENTS.AUDIT))),
    **dict(
        zip(
            EVENTS.OPEN_FORUM,
            [("on_open_forum", EVENTS_ENUM.OPEN_FORUM)] * len(EVENTS.OPEN_FORUM),
        )
    ),
    **dict(zip(EVENTS.AUDIO, [("on_audio", EVENTS_ENUM.AUDIO)] * len(EVENTS.AUDIO))),
    **dict(
        zip(
            EVENTS.ALC_MEMBER,
            [("on_live_channel_member", EVENTS_ENUM.ALC_MEMBER)]
            * len(EVENTS.ALC_MEMBER),
        )
    ),
    **dict(
        zip(
            EVENTS.GROUP,
            [("on_group_event", EVENTS_ENUM.GROUP)] * len(EVENTS.GROUP),
        )
    ),
    **dict(
        zip(
            EVENTS.FRIEND,
            [("on_friend_event", EVENTS_ENUM.FRIEND)] * len(EVENTS.FRIEND),
        )
    ),
}

EVENTS_TO_MODEL = {
    **dict(
        zip(
            EVENTS.MESSAGE_CREATE,
            [Model.MESSAGE] * len(EVENTS.MESSAGE_CREATE),
        )
    ),
    **dict(
        zip(
            EVENTS.DM_CREATE,
            [Model.DIRECT_MESSAGE] * len(EVENTS.DM_CREATE),
        )
    ),
    **dict(
        zip(
            EVENTS.C2C_MESSAGE_CREATE,
            [Model.C2C_MESSAGE] * len(EVENTS.C2C_MESSAGE_CREATE),
        )
    ),
    **dict(
        zip(
            EVENTS.GROUP_AT_MESSAGE_CREATE,
            [Model.GROUP_MESSAGE] * len(EVENTS.GROUP_AT_MESSAGE_CREATE),
        )
    ),
    **dict(
        zip(
            EVENTS.MESSAGE_DELETE,
            [Model.MESSAGE_DELETE] * len(EVENTS.MESSAGE_DELETE),
        )
    ),
    **dict(
        zip(
            EVENTS.FORUM,
            [Model.FORUMS_EVENT] * len(EVENTS.FORUM),
        )
    ),
    **dict(
        zip(
            EVENTS.GUILD,
            [Model.GUILDS] * len(EVENTS.GUILD),
        )
    ),
    **dict(
        zip(
            EVENTS.CHANNEL,
            [Model.CHANNELS] * len(EVENTS.CHANNEL),
        )
    ),
    **dict(
        zip(
            EVENTS.GUILD_MEMBER,
            [Model.GUILD_MEMBERS] * len(EVENTS.GUILD_MEMBER),
        )
    ),
    **dict(
        zip(
            EVENTS.REACTION,
            [Model.REACTION] * len(EVENTS.REACTION),
        )
    ),
    **dict(
        zip(
            EVENTS.INTERACTION,
            [Model.INTERACTION] * len(EVENTS.INTERACTION),
        )
    ),
    **dict(
        zip(
            EVENTS.AUDIT,
            [Model.MESSAGE_AUDIT] * len(EVENTS.AUDIT),
        )
    ),
    **dict(
        zip(
            EVENTS.OPEN_FORUM,
            [Model.OPEN_FORUMS] * len(EVENTS.OPEN_FORUM),
        )
    ),
    **dict(
        zip(
            EVENTS.AUDIO,
            [Model.AUDIO_ACTION] * len(EVENTS.AUDIO),
        )
    ),
    **dict(
        zip(
            EVENTS.ALC_MEMBER,
            [Model.LIVE_CHANNEL_MEMBER] * len(EVENTS.ALC_MEMBER),
        )
    ),
    **dict(
        zip(
            EVENTS.GROUP,
            [Model.GROUP_EVENTS] * len(EVENTS.GROUP),
        )
    ),
    **dict(
        zip(
            EVENTS.FRIEND,
            [Model.FRIEND_EVENTS] * len(EVENTS.FRIEND),
        )
    ),
}
