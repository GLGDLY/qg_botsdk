# !/usr/bin/env python3
# encoding: utf-8
from inspect import stack
from typing import List
from re import split as re_split

apis = {('获取用户ID', 'get_bot_id'): [False, '此API不需要请求权限'],
        ('获取用户信息', 'get_bot_info'): ['GET', '/users/@me'],
        ('获取用户频道列表', 'get_bot_guilds'): ['GET', '/users/@me/guilds'],
        ('获取频道详情', 'get_guild_info'): ['GET', '/guilds/{guild_id}'],
        ('获取子频道列表', 'get_guild_channels'): ['GET', '/guilds/{guild_id}/channels'],
        ('获取子频道详情', 'get_channels_info'): ['GET', '/channels/{channel_id}'],
        ('创建子频道', 'create_channels'): ['POST', '/guilds/{guild_id}/channels'],
        ('修改子频道', 'patch_channels'): ['PATCH', '/channels/{channel_id}'],
        ('删除子频道', 'delete_channels'): ['DELETE', '/channels/{channel_id}'],
        ('获取频道成员列表', 'get_guild_members'): ['GET', '/guilds/{guild_id}/members'],
        ('获取频道成员详情', 'get_member_info'): ['GET', '/guilds/{guild_id}/members/{user_id}'],
        ('删除频道成员', 'delete_member'): ['DELETE', '/guilds/{guild_id}/members/{user_id}'],
        ('获取频道身份组列表', 'get_guild_roles'): ['GET', '/guilds/{guild_id}/roles'],
        ('创建频道身份组', 'create_role'): ['POST', '/guilds/{guild_id}/roles'],
        ('修改频道身份组', 'patch_role'): ['PATCH', '/guilds/{guild_id}/roles/{role_id}'],
        ('删除频道身份组', 'delete_role'): ['DELETE', '/guilds/{guild_id}/roles/{role_id}'],
        ('创建频道身份组成员', 'create_role_member'): ['PUT', '/guilds/{guild_id}/members/{user_id}/roles/{role_id}'],
        ('删除频道身份组成员', 'delete_role_member'): ['DELETE', '/guilds/{guild_id}/members/{user_id}/roles/{role_id}'],
        ('获取子频道用户权限', 'get_channel_member_permission'):
            ['GET', '/channels/{channel_id}/members/{user_id}/permissions'],
        ('修改子频道用户权限', 'put_channel_member_permission'):
            ['PUT', '/channels/{channel_id}/members/{user_id}/permissions'],
        ('获取子频道身份组权限', 'get_channel_role_permission'):
            ['GET', '/channels/{channel_id}/roles/{role_id}/permissions'],
        ('修改子频道身份组权限', 'put_channel_role_permission'):
            ['PUT', '/channels/{channel_id}/roles/{role_id}/permissions'],
        ('获取指定消息', 'get_message_info'): ['GET', '/channels/{channel_id}/messages/{message_id}'],
        ('发送普通消息', 'send_msg', '发送embed模板消息', 'send_embed', '发送 23 链接+文本列表模板ark消息', 'send_ark_23',
         '发送 24 文本+缩略图模板ark消息', 'send_ark_24', '发送 37 大图模板ark消息', 'send_ark_37'):
            ['POST', '/channels/{channel_id}/messages'],
        ('撤回消息', 'delete_msg'): ['DELETE', '/channels/{channel_id}/messages/{message_id}'],
        ('获取频道消息频率设置', 'get_guild_setting'): ['GET', '/guilds/{guild_id}/message/setting'],
        ('创建私信会话', 'create_dm_guild'): ['POST', '/users/@me/dms'],
        ('发送私信消息', 'send_dm'): ['POST', '/dms/{guild_id}/messages'],
        ('撤回私信消息', 'delete_dm_msg'): ['DELETE', '/dms/{guild_id}/messages/{message_id}'],
        ('禁言全员', 'mute_all_member'): ['PATCH', '/guilds/{guild_id}/mute'],
        ('禁言指定成员', 'mute_member'): ['PATCH', '/guilds/{guild_id}/members/{user_id}/mute'],
        ('禁言批量成员', 'mute_members'): ['PATCH', '/guilds/{guild_id}/mute'],
        ('创建频道公告', 'create_announce'): ['POST', '/guilds/{guild_id}/announces'],
        ('删除频道公告', 'delete_announce'): ['DELETE', '/guilds/{guild_id}/announces/{message_id}'],
        ('添加精华消息', 'create_pinmsg'): ['PUT', '/channels/{channel_id}/pins/{message_id}'],
        ('删除精华消息', 'delete_pinmsg'): ['DELETE', '/channels/{channel_id}/pins/{message_id}'],
        ('获取精华消息', 'get_pinmsg'): ['GET', '/channels/{channel_id}/pins'],
        ('获取频道日程列表', 'get_schedules'): ['GET', '/channels/{channel_id}/schedules'],
        ('获取日程详情', 'get_schedule_info'): ['GET', '/channels/{channel_id}/schedules/{schedule_id}'],
        ('创建日程', 'create_schedule'): ['POST', '/channels/{channel_id}/schedules'],
        ('修改日程', 'patch_schedule'): ['PATCH', '/channels/{channel_id}/schedules/{schedule_id}'],
        ('删除日程', 'delete_schedule'): ['DELETE', '/channels/{channel_id}/schedules/{schedule_id}'],
        ('发表表情表态', 'create_reaction'):
            ['PUT', '/channels/{channel_id}/messages/{message_id}/reactions/{type}/{id}'],
        ('删除表情表态', 'delete_reaction'):
            ['DELETE', '/channels/{channel_id}/messages/{message_id}/reactions/{type}/{id}'],
        ('拉取表情表态用户列表', 'get_reaction_users'):
            ['GET', '/channels/{channel_id}/messages/{message_id}/reactions/{type}/{id}'],
        ('音频控制', 'control_audio'): ['POST', '/channels/{channel_id}/audio'],
        ('机器人上麦', 'bot_on_mic'): ['PUT', '/channels/{channel_id}/mic'],
        ('机器人下麦', 'bot_off_mic'): ['DELETE', '/channels/{channel_id}/mic'],
        ('获取帖子列表', 'get_threads'): ['GET', '/channels/{channel_id}/threads'],
        ('获取帖子详情', 'get_thread_info'): ['GET', '/channels/{channel_id}/threads/{thread_id}'],
        ('发表帖子', 'create_thread'): ['PUT', '/channels/{channel_id}/threads'],
        ('删除帖子', 'delete_thread'): ['DELETE', '/channels/{channel_id}/threads/{thread_id}'],
        ('获取频道可用权限列表', 'get_guild_permissions', '创建频道 API 接口权限授权链接', 'create_permission_demand'):
            [False, '此API不需要请求权限']}


def __getattr__(identifier: str) -> object:
    if re_split(r'[/\\]', stack()[1].filename)[-1] not in ('qg_bot.py', 'api.py', 'async_api.py'):
        raise AssertionError("此为SDK内部使用文件，无法使用，使用机器人Model库请from model import Model")

    return globals()[identifier.__path__]


def api_converter(api: str):
    if api[-2:] in ['()', '（）']:
        api = api[:-2]
    for keys, values in apis.items():
        if api in keys:
            return values[0], values[1]
    return False, '该API并不存在'


def api_converter_re(method: str, path: str):
    for keys, values in apis.items():
        if [method, path] == values:
            return keys[1]
    return None


class ReplyModel:
    def __init__(self, type_: object or dict = object):
        if re_split(r'[/\\]', stack()[1].filename)[-1] not in ('qg_bot.py', 'api.py', 'async_api.py'):
            raise AssertionError('ReplyModel()为SDK内部使用类，无法使用')
        self.type_ = type_

    class _EmptyReturnTemplate:
        code: int
        message: str

    def robot(self):
        class Robot:
            id: str
            username: str
            avatar: str

        return Robot

    def get_bot_info(self):
        class GetBotInfo:
            class data:
                id: str
                username: str
                avatar: str
                union_openid: str
                union_user_account: str
                code: int
                message: str

            http_code: int
            trace_id: str
            result: bool

        return GetBotInfo

    def get_bot_guilds(self):
        class GetBotGuilds:
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

    def get_guild_info(self):
        class GetGuildInfo:
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

    def get_guild_channels(self):
        class GetGuildChannels:
            class __channels:
                id: str
                guild_id: str
                name: str
                type: int
                position: int
                parent_id: str
                owner_id: str
                sub_type: int
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
        op_user_id: str or None
        sub_type: int
        private_type: int
        private_user_ids: List[str]
        speak_permission: int
        application_id: str
        permissions: str
        code: int
        message: str

    def get_channels_info(self):
        channels = self._Channels

        class GetChannelsInfo:
            data: channels
            http_code: int
            trace_id: str
            result: bool

        return GetChannelsInfo

    def create_channels(self):
        channels = self._Channels

        class CreateChannels:
            data: channels
            http_code: int
            trace_id: str
            result: bool

        return CreateChannels

    def patch_channels(self):
        channels = self._Channels

        class PatchChannels:
            data: channels
            http_code: int
            trace_id: str
            result: bool

        return PatchChannels

    def delete_channels(self):
        temp = self._EmptyReturnTemplate

        class DeleteChannels:
            data: temp
            http_code: int
            trace_id: str
            result: bool

        return DeleteChannels

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

    def get_guild_members(self):
        member = self._Member

        class GetGuildMembers:
            data: List[member]
            http_code: List[int]
            trace_id: List[str]
            result: List[bool]

        return GetGuildMembers

    def get_member_info(self):
        member = self._Member

        class GetMemberInfo:
            data: member
            http_code: int
            trace_id: str
            result: bool

        return GetMemberInfo

    def delete_member(self):
        temp = self._EmptyReturnTemplate

        class DeleteMember:
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

    def get_guild_roles(self):
        role_ = self._Role

        class GetGuildRoles:
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

    def create_role(self):
        role_ = self._Role

        class CreateRole:
            class data:
                role_id: str
                role: role_
                code: int
                message: str

            http_code: int
            trace_id: str
            result: bool

        return CreateRole

    def patch_role(self):
        role_ = self._Role

        class PatchRole:
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

    def delete_role(self):
        temp = self._EmptyReturnTemplate

        class DeleteRole:
            data: temp
            http_code: int
            trace_id: str
            result: bool

        return DeleteRole

    def role_members(self):
        class RoleMembers:
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

    def get_channel_member_permission(self):
        permission = self._Permission_Mem

        class GetChannelMemberPermission:
            data: permission
            http_code: int
            trace_id: str
            result: bool

        return GetChannelMemberPermission

    def put_channel_mr_permission(self):
        temp = self._EmptyReturnTemplate

        class PutChannelMRPermission:
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

    def get_channel_role_permission(self):
        permission = self._Permission_Role

        class GetChannelRolePermission:
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
        attachments = [__MsgAttachments]
        timestamp: str
        code: int
        message: str

    def get_message_info(self):
        message_ = self._Message

        class GetMessageInfo:
            class data:
                message: message_

            http_code: int
            trace_id: str
            result: bool

        return GetMessageInfo

    def send_msg(self):
        class SendMsg:
            class data:
                id: str
                channel_id: str
                guild_id: str
                content: str
                timestamp: str
                tts: bool
                mention_everyone: bool
                author: dict
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

    def delete_msg(self):
        temp = self._EmptyReturnTemplate

        class DeleteMsg:
            data: temp
            http_code: int
            trace_id: str
            result: bool

        return DeleteMsg

    def get_guild_setting(self):
        class GetGuildSetting:
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

    def create_dm_guild(self):
        class CreateDmGuild:
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

    def mute_member(self):
        temp = self._EmptyReturnTemplate

        class MuteMember:
            data: temp
            http_code: int
            trace_id: str
            result: bool

        return MuteMember

    def mute_members(self):
        class MuteMembers:
            class data:
                user_ids: List[str]
                code: int
                message: str

            http_code: int
            trace_id: str
            result: bool

        return MuteMembers

    def create_announce(self):
        class RecommendChannels:
            channel_id: str
            introduce: str

        class CreateAnnounce:
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

    def delete_announce(self):
        temp = self._EmptyReturnTemplate

        class DeleteAnnounce:
            data: temp
            http_code: int
            trace_id: str
            result: bool

        return DeleteAnnounce

    def pinmsg(self):
        class PinMsg:
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

    def delete_pinmsg(self):
        temp = self._EmptyReturnTemplate

        class DeletePinMsg:
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

    def get_schedules(self):
        schedule = self.__Schedule

        class GetSchedules:
            data: [schedule]
            http_code: int
            trace_id: str
            result: bool

        return GetSchedules

    def schedule_info(self):
        schedule = self.__Schedule

        class ScheduleInfo:
            data: schedule
            http_code: int
            trace_id: str
            result: bool

        return ScheduleInfo

    def delete_schedule(self):
        temp = self._EmptyReturnTemplate

        class DeleteSchedule:
            data: temp
            http_code: int
            trace_id: str
            result: bool

        return DeleteSchedule

    def reactions(self):
        temp = self._EmptyReturnTemplate

        class Reactions:
            data: temp
            http_code: int
            trace_id: str
            result: bool

        return Reactions

    def get_reaction_users(self):
        class Users:
            id: str
            username: str
            avatar: str
            code: int
            message: str

        class GetReactionUsers:
            data: List[Users]
            http_code: List[int]
            trace_id: List[str]
            result: List[bool]

        return GetReactionUsers

    def audio(self):
        temp = self._EmptyReturnTemplate

        class Audio:
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
                        class text:   # type = 1
                            text: str

                        class image:   # type = 2
                            class plat_image:
                                url: str
                                width: int
                                height: int
                                image_id: str

                        class video:   # type = 3
                            class plat_video:
                                class cover:
                                    url: str
                                    width: int
                                    height: int
                                url: str
                                width: int
                                height: int
                                video_id: str

                        class url:   # type = 4
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

    def get_threads(self):
        thread = self.__Threads

        class GetThreads:
            data: List[thread]
            http_code: List[int]
            trace_id: List[str]
            result: List[bool]

        return GetThreads

    def get_thread_info(self):
        thread = self.__Threads

        class GetThreadInfo:
            data: thread
            http_code: int
            trace_id: str
            result: bool

        return GetThreadInfo

    def create_thread(self):
        class CreateThread:
            class data:
                task_id: str
                create_time: str
                code: int
                message: str

            http_code: int
            trace_id: str
            result: bool
        return CreateThread

    def delete_thread(self):
        temp = self._EmptyReturnTemplate

        class DeleteThread:
            data: temp
            http_code: int
            trace_id: str
            result: bool

        return DeleteThread

    def get_guild_permissions(self):
        class Api:
            api: str
            path: str
            method: str
            desc: str
            auth_status: int

        class GetGuildPermissions:
            class data:
                apis = [Api]
                code: int
                message: str

            http_code: int
            trace_id: str
            result: bool
        return GetGuildPermissions

    def create_permission_demand(self):
        class CreatePermissionDemand:
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
