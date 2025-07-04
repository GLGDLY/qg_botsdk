#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ._event import object_class

apis = {
    ("获取用户ID", "get_bot_id"): [False, "此API不需要请求权限"],
    ("获取用户信息", "get_bot_info"): ["GET", "/users/@me"],
    ("获取用户频道列表", "get_bot_guilds"): ["GET", "/users/@me/guilds"],
    ("获取频道详情", "get_guild_info"): ["GET", "/guilds/{guild_id}"],
    ("获取子频道列表", "get_guild_channels"): ["GET", "/guilds/{guild_id}/channels"],
    ("获取子频道详情", "get_channels_info"): ["GET", "/channels/{channel_id}"],
    ("创建子频道", "create_channels"): ["POST", "/guilds/{guild_id}/channels"],
    ("修改子频道", "patch_channels"): ["PATCH", "/channels/{channel_id}"],
    ("删除子频道", "delete_channels"): ["DELETE", "/channels/{channel_id}"],
    ("获取在线成员数", "get_online_nums"): [
        "GET",
        "/channels/{channel_id}/online_nums",
    ],
    ("获取频道成员列表", "get_guild_members"): ["GET", "/guilds/{guild_id}/members"],
    ("获取频道身份组成员列表", "get_role_members"): [
        "GET",
        "/guilds/{guild_id}/roles/{role_id}/members",
    ],
    ("获取频道成员详情", "get_member_info"): [
        "GET",
        "/guilds/{guild_id}/members/{user_id}",
    ],
    ("删除频道成员", "delete_member"): [
        "DELETE",
        "/guilds/{guild_id}/members/{user_id}",
    ],
    ("获取频道身份组列表", "get_guild_roles"): ["GET", "/guilds/{guild_id}/roles"],
    ("创建频道身份组", "create_role"): ["POST", "/guilds/{guild_id}/roles"],
    ("修改频道身份组", "patch_role"): ["PATCH", "/guilds/{guild_id}/roles/{role_id}"],
    ("删除频道身份组", "delete_role"): ["DELETE", "/guilds/{guild_id}/roles/{role_id}"],
    ("创建频道身份组成员", "create_role_member"): [
        "PUT",
        "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
    ],
    ("删除频道身份组成员", "delete_role_member"): [
        "DELETE",
        "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
    ],
    ("获取子频道用户权限", "get_channel_member_permission"): [
        "GET",
        "/channels/{channel_id}/members/{user_id}/permissions",
    ],
    ("修改子频道用户权限", "put_channel_member_permission"): [
        "PUT",
        "/channels/{channel_id}/members/{user_id}/permissions",
    ],
    ("获取子频道身份组权限", "get_channel_role_permission"): [
        "GET",
        "/channels/{channel_id}/roles/{role_id}/permissions",
    ],
    ("修改子频道身份组权限", "put_channel_role_permission"): [
        "PUT",
        "/channels/{channel_id}/roles/{role_id}/permissions",
    ],
    ("获取指定消息", "get_message_info"): [
        "GET",
        "/channels/{channel_id}/messages/{message_id}",
    ],
    (
        "发送普通消息",
        "send_msg",
        "发送embed模板消息",
        "send_embed",
        "发送 23 链接+文本列表模板ark消息",
        "send_ark_23",
        "发送 24 文本+缩略图模板ark消息",
        "send_ark_24",
        "发送 37 大图模板ark消息",
        "send_ark_37",
    ): ["POST", "/channels/{channel_id}/messages"],
    ("撤回消息", "delete_msg"): [
        "DELETE",
        "/channels/{channel_id}/messages/{message_id}",
    ],
    ("获取频道消息频率设置", "get_guild_setting"): [
        "GET",
        "/guilds/{guild_id}/message/setting",
    ],
    ("创建私信会话", "create_dm_guild"): ["POST", "/users/@me/dms"],
    ("发送私信消息", "send_dm"): ["POST", "/dms/{guild_id}/messages"],
    ("撤回私信消息", "delete_dm_msg"): [
        "DELETE",
        "/dms/{guild_id}/messages/{message_id}",
    ],
    ("禁言全员", "mute_all_member"): ["PATCH", "/guilds/{guild_id}/mute"],
    ("禁言指定成员", "mute_member"): [
        "PATCH",
        "/guilds/{guild_id}/members/{user_id}/mute",
    ],
    ("禁言批量成员", "mute_members"): ["PATCH", "/guilds/{guild_id}/mute"],
    ("创建频道公告", "create_announce"): ["POST", "/guilds/{guild_id}/announces"],
    ("删除频道公告", "delete_announce"): [
        "DELETE",
        "/guilds/{guild_id}/announces/{message_id}",
    ],
    ("添加精华消息", "create_pinmsg"): [
        "PUT",
        "/channels/{channel_id}/pins/{message_id}",
    ],
    ("删除精华消息", "delete_pinmsg"): [
        "DELETE",
        "/channels/{channel_id}/pins/{message_id}",
    ],
    ("获取精华消息", "get_pinmsg"): ["GET", "/channels/{channel_id}/pins"],
    ("获取频道日程列表", "get_schedules"): ["GET", "/channels/{channel_id}/schedules"],
    ("获取日程详情", "get_schedule_info"): [
        "GET",
        "/channels/{channel_id}/schedules/{schedule_id}",
    ],
    ("创建日程", "create_schedule"): ["POST", "/channels/{channel_id}/schedules"],
    ("修改日程", "patch_schedule"): [
        "PATCH",
        "/channels/{channel_id}/schedules/{schedule_id}",
    ],
    ("删除日程", "delete_schedule"): [
        "DELETE",
        "/channels/{channel_id}/schedules/{schedule_id}",
    ],
    ("发表表情表态", "create_reaction"): [
        "PUT",
        "/channels/{channel_id}/messages/{message_id}/reactions/{type}/{id}",
    ],
    ("删除表情表态", "delete_reaction"): [
        "DELETE",
        "/channels/{channel_id}/messages/{message_id}/reactions/{type}/{id}",
    ],
    ("拉取表情表态用户列表", "get_reaction_users"): [
        "GET",
        "/channels/{channel_id}/messages/{message_id}/reactions/{type}/{id}",
    ],
    ("音频控制", "control_audio"): ["POST", "/channels/{channel_id}/audio"],
    ("机器人上麦", "bot_on_mic"): ["PUT", "/channels/{channel_id}/mic"],
    ("机器人下麦", "bot_off_mic"): ["DELETE", "/channels/{channel_id}/mic"],
    ("获取帖子列表", "get_threads"): ["GET", "/channels/{channel_id}/threads"],
    ("获取帖子详情", "get_thread_info"): [
        "GET",
        "/channels/{channel_id}/threads/{thread_id}",
    ],
    ("发表帖子", "create_thread"): ["PUT", "/channels/{channel_id}/threads"],
    ("删除帖子", "delete_thread"): [
        "DELETE",
        "/channels/{channel_id}/threads/{thread_id}",
    ],
    (
        "[单聊]单独发动消息给用户",
        "send_friend_msg",
    ): ["POST", "/v2/users/{openid}/messages"],
    (
        "[群聊]发送消息到群聊",
        "send_group_msg",
    ): ["POST", "/v2/groups/{group_openid}/messages"],
    (
        "获取频道可用权限列表",
        "get_guild_permissions",
        "创建频道 API 接口权限授权链接",
        "create_permission_demand",
    ): [False, "此API不需要请求权限"],
    ("互动事件回调", "callback_interactions"): [
        "PUT",
        "/interactions/{interaction_id}",
    ],
}


def api_converter(api: str):
    if api[-2:] in ["()", "（）"]:
        api = api[:-2]
    for keys, values in apis.items():
        if api in keys:
            return values[1], values[0]
    return False, "该API并不存在"


def api_converter_re(method: str, path: str):
    for keys, values in apis.items():
        if [method, path] == values:
            return keys[1]


class _EmptyReturnTemplate:
    code: int
    message: str


def robot_model():
    class Robot:
        id: str
        username: str
        avatar: str
        union_openid: str
        union_user_account: str
        code: int
        message: str

    return Robot


def get_bot_info():
    class GetBotInfo(object_class):
        data: robot_model()
        http_code: int
        trace_id: str
        result: bool

    return GetBotInfo


def get_bot_guilds():
    class GetBotGuilds(object_class):
        class __guild:
            id: str
            name: str
            icon: str
            owner_id: str
            owner: bool
            joined_at: str
            member_count: str
            max_members: str
            description: str
            code: int
            message: str

        data: List[__guild]
        http_code: List[int]
        trace_id: List[str]
        result: List[bool]

    return GetBotGuilds


def get_guild_info():
    class GetGuildInfo(object_class):
        class data:
            id: str
            name: str
            icon: str
            owner_id: str
            owner: bool
            joined_at: str
            member_count: int
            max_members: int
            description: str
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return GetGuildInfo


def get_guild_channels():
    class GetGuildChannels(object_class):
        class __channels:
            id: str
            guild_id: str
            name: str
            type: int
            position: int
            parent_id: str
            owner_id: str
            sub_type: int
            private_type: int
            speak_permission: int
            application_id: str
            permissions: str
            code: int
            message: str

        data: List[__channels]
        http_code: int
        trace_id: str
        result: bool

    return GetGuildChannels


class _Channels:
    id: str
    guild_id: str
    name: str
    type: int
    position: int
    parent_id: str
    owner_id: str
    op_user_id: Optional[str]
    sub_type: int
    private_type: int
    private_user_ids: List[str]
    speak_permission: int
    application_id: str
    permissions: str
    code: int
    message: str


def get_channels_info():
    channels = _Channels

    class GetChannelsInfo(object_class):
        data: channels
        http_code: int
        trace_id: str
        result: bool

    return GetChannelsInfo


def create_channels():
    channels = _Channels

    class CreateChannels(object_class):
        data: channels
        http_code: int
        trace_id: str
        result: bool

    return CreateChannels


def patch_channels():
    channels = _Channels

    class PatchChannels(object_class):
        data: channels
        http_code: int
        trace_id: str
        result: bool

    return PatchChannels


def delete_channels():
    temp = _EmptyReturnTemplate

    class DeleteChannels(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return DeleteChannels


def get_online_nums():
    class GetOnlineNums(object_class):
        class data:
            online_nums: int

        http_code: int
        trace_id: str
        result: bool

    return GetOnlineNums


class _Member:
    class user:
        id: str
        username: str
        avatar: str
        bot: bool

    nick: str
    roles: List[str]
    joined_at: str
    deaf: bool
    mute: bool
    pending: bool
    code: int
    message: str


def get_guild_members():
    class GetGuildMembers(object_class):
        data: List[_Member]
        http_code: List[int]
        trace_id: List[str]
        result: List[bool]

    return GetGuildMembers


def get_role_members():
    class GetRoleMembers(object_class):
        data: List[_Member]
        http_code: List[int]
        trace_id: List[str]
        result: List[bool]

    return GetRoleMembers


def get_member_info():
    class GetMemberInfo(object_class):
        data: _Member
        http_code: int
        trace_id: str
        result: bool

    return GetMemberInfo


def delete_member():
    temp = _EmptyReturnTemplate

    class DeleteMember(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return DeleteMember


class _Role:
    id: str
    name: str
    color: int
    hoist: int
    number: int
    member_limit: int


def get_guild_roles():
    role_ = _Role

    class GetGuildRoles(object_class):
        class data:
            guild_id: str
            roles: List[role_]
            role_num_limit: str
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return GetGuildRoles


def create_role():
    role_ = _Role

    class CreateRole(object_class):
        class data:
            role_id: str
            role: role_
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return CreateRole


def patch_role():
    role_ = _Role

    class PatchRole(object_class):
        class data:
            guild_id: str
            role_id: str
            role: role_
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return PatchRole


def delete_role():
    temp = _EmptyReturnTemplate

    class DeleteRole(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return DeleteRole


def role_members():
    class RoleMembers(object_class):
        class data:
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return RoleMembers


class _Permission_Mem:
    channel_id: str
    user_id: str
    permissions: str
    code: int
    message: str


def get_channel_member_permission():
    permission = _Permission_Mem

    class GetChannelMemberPermission(object_class):
        data: permission
        http_code: int
        trace_id: str
        result: bool

    return GetChannelMemberPermission


def put_channel_mr_permission():
    temp = _EmptyReturnTemplate

    class PutChannelMRPermission(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return PutChannelMRPermission


class _Permission_Role:
    channel_id: str
    role_id: str
    permissions: str
    code: int
    message: str


def get_channel_role_permission():
    permission = _Permission_Role

    class GetChannelRolePermission(object_class):
        data: permission
        http_code: int
        trace_id: str
        result: bool

    return GetChannelRolePermission


class _Message:
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
        bot: bool
        id: str
        username: str

    class member:
        joined_at: str
        roles: List[str]

    channel_id: str
    guild_id: str
    content: str
    id: str
    attachments = List[__MsgAttachments]
    timestamp: str
    code: int
    message: str


def get_message_info():
    message_ = _Message

    class GetMessageInfo(object_class):
        class data:
            message: message_

        http_code: int
        trace_id: str
        result: bool

    return GetMessageInfo


def send_msg():
    class SendMsg(object_class):
        class data:
            id: str
            channel_id: str
            guild_id: str
            content: str
            timestamp: str
            tts: bool
            mention_everyone: bool
            author: Dict
            pinned: bool
            type: int
            flags: int
            seq_in_channel: str
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return SendMsg


def delete_msg():
    temp = _EmptyReturnTemplate

    class DeleteMsg(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return DeleteMsg


def get_guild_setting():
    class GetGuildSetting(object_class):
        class data:
            disable_create_dm: bool
            disable_push_msg: bool
            channel_ids: List[str]
            channel_push_max_num: int
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return GetGuildSetting


def create_dm_guild():
    class CreateDmGuild(object_class):
        class data:
            guild_id: str
            channel_id: str
            create_time: str
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return CreateDmGuild


def mute_member():
    temp = _EmptyReturnTemplate

    class MuteMember(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return MuteMember


def mute_members():
    class MuteMembers(object_class):
        class data:
            user_ids: List[str]
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return MuteMembers


def create_announce():
    class RecommendChannels:
        channel_id: str
        introduce: str

    class CreateAnnounce(object_class):
        class data:
            guild_id: str
            channel_id: str
            message_id: str
            announces_type: int
            recommend_channels: List[RecommendChannels]
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return CreateAnnounce


def delete_announce():
    temp = _EmptyReturnTemplate

    class DeleteAnnounce(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return DeleteAnnounce


def pinmsg():
    class PinMsg(object_class):
        class data:
            guild_id: str
            channel_id: str
            message_ids: List[str]
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return PinMsg


def delete_pinmsg():
    temp = _EmptyReturnTemplate

    class DeletePinMsg(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return DeletePinMsg


class __Schedule:
    class creator:
        class user:
            id: str
            username: str
            bot: bool

        nick: str
        joined_at: str

    id: str
    name: str
    description: str
    start_timestamp: str
    end_timestamp: str
    jump_channel_id: str
    remind_type: str
    code: int
    message: str


def get_schedules():
    schedule = __Schedule

    class GetSchedules(object_class):
        data: List[schedule]
        http_code: int
        trace_id: str
        result: bool

    return GetSchedules


def schedule_info():
    schedule = __Schedule

    class ScheduleInfo(object_class):
        data: schedule
        http_code: int
        trace_id: str
        result: bool

    return ScheduleInfo


def delete_schedule():
    temp = _EmptyReturnTemplate

    class DeleteSchedule(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return DeleteSchedule


def reactions():
    temp = _EmptyReturnTemplate

    class Reactions(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return Reactions


def get_reaction_users():
    class Users:
        id: str
        username: str
        avatar: str
        code: int
        message: str

    class GetReactionUsers(object_class):
        data: List[Users]
        http_code: List[int]
        trace_id: List[str]
        result: List[bool]

    return GetReactionUsers


def audio():
    temp = _EmptyReturnTemplate

    class Audio(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return Audio


class __Threads:
    class thread_info:
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

                elems: List[__ForumsSubContent]
                props: object

            paragraphs: List[__ForumsContent]

        thread_id: str
        title: str
        date_time: str

    guild_id: str
    channel_id: str
    author_id: str
    code: int
    message: str


def get_threads():
    thread = __Threads

    class GetThreads(object_class):
        data: List[thread]
        http_code: List[int]
        trace_id: List[str]
        result: List[bool]

    return GetThreads


def get_thread_info():
    thread = __Threads

    class GetThreadInfo(object_class):
        data: thread
        http_code: int
        trace_id: str
        result: bool

    return GetThreadInfo


def create_thread():
    class CreateThread(object_class):
        class data:
            task_id: str
            create_time: str
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return CreateThread


def delete_thread():
    temp = _EmptyReturnTemplate

    class DeleteThread(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return DeleteThread


def get_guild_permissions():
    class Api:
        api: str
        path: str
        method: str
        desc: str
        auth_status: int

    class GetGuildPermissions(object_class):
        class data:
            apis = List[Api]
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return GetGuildPermissions


def create_permission_demand():
    class CreatePermissionDemand(object_class):
        class data:
            class api_identify:
                path: str
                method: str

            guild_id: str
            channel_id: str
            title: str
            desc: str
            code: int
            message: str

        http_code: int
        trace_id: str
        result: bool

    return CreatePermissionDemand


def upload_media():
    class UploadMedia(object_class):
        class data:
            file_uuid: str
            file_info: str
            ttl: int

        http_code: int
        trace_id: str
        result: bool

    return UploadMedia


def callback_interactions():
    temp = _EmptyReturnTemplate

    class Callback_interactions(object_class):
        data: temp
        http_code: int
        trace_id: str
        result: bool

    return Callback_interactions


# API related
class StrPtr:
    def __init__(self, value: Optional[str] = None):
        self.value = value

    def get(self):
        return self.value if self.value is not None else ""

    def __repr__(self):
        return f'<StrPtr "{self.value}">'

    def __json__(self):
        return str(self.value) if self.value is not None else None


class MessageConstructRet:
    def __init__(
        self,
        result: bool,
        logger_msg: Optional[str] = None,
        error_ret: Optional[send_msg()] = None,
        kwargs: Optional[dict] = None,
    ):
        self.result = result
        self.logger_msg = logger_msg
        self.error_ret = error_ret
        self.kwargs = kwargs


class BaseMessageApiModel(ABC):
    def __init__(self):
        self._message_id, self._event_id = StrPtr(), StrPtr()
        self._msg_seq = 0
        self._msg_type = 0
        self._constructed_obj: Optional[MessageConstructRet] = None

    def update(self, **kwargs):
        for k, v in kwargs.items():
            # print(k, v)
            k = f"_{k}"
            # print(hasattr(self, k))
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise AttributeError(f"BaseMessageApiModel has no attribute {k}")
        self._constructed_obj = self._construct(self._message_id, self._event_id)

    @abstractmethod
    def __repr__(self):
        return "<BaseMessage abstract class>"

    @abstractmethod
    def _construct(self, message_id, event_id) -> MessageConstructRet:
        pass

    def get_msg_seq(self):
        """
        获取消息序号（仅qq单聊或群消息等v2消息API）
        """
        return self._msg_seq

    def construct(
        self, message_id, event_id, is_v2: bool = False, msg_seq: Optional[int] = None
    ) -> MessageConstructRet:
        self._message_id.value = message_id
        self._event_id.value = event_id
        if is_v2 and self._constructed_obj and self._constructed_obj.kwargs:
            k = None
            for _k in self._constructed_obj.kwargs.keys():
                k = _k
                break
            if k:
                params = {}
                if msg_seq is not None and isinstance(msg_seq, int):
                    self._msg_seq = msg_seq
                else:
                    self._msg_seq += 1
                params["msg_seq"] = self._msg_seq
                if (
                    self._msg_type == 0
                    and hasattr(self, "_media_file_info")
                    and self._media_file_info
                ):
                    params["msg_type"] = 7
                else:
                    params["msg_type"] = self._msg_type

                if isinstance(self._constructed_obj.kwargs[k], dict):
                    for _k, _v in params.items():
                        self._constructed_obj.kwargs[k][_k] = _v
                else:
                    try:
                        for _k, _v in params.items():
                            self._constructed_obj.kwargs[k].add_field(_k, str(_v))
                    except Exception:
                        pass
        return self._constructed_obj
