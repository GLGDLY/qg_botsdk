#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from asyncio import AbstractEventLoop, run_coroutine_threadsafe
from time import sleep, time
from typing import BinaryIO, Dict, Iterable, List, Optional, Tuple, Union

from . import _api_model, model
from ._exception import WaitError, WaitTimeoutError
from ._statics import TraceNames
from ._utils import TraceCallerData
from .api_model import BaseMessageApiModel
from .async_api import AsyncAPI


class API:
    def __init__(
        self, api: AsyncAPI, loop: AbstractEventLoop, timeout: int, session_manager
    ):
        self._api = api
        self._loop = loop
        self._timeout = timeout
        self.__session_manager = session_manager
        self.__session_manager.api = self

    # sdk internal api
    def wait_for(
        self,
        scope: Union[model.Scope, Iterable[model.Scope]],
        command_obj: model.BotCommandObject,
        timeout: int = None,
    ) -> model.Model.MESSAGE:
        """
        等待指定的command被触发

        :param scope: 指定的校验作用域或作用域列表(USER, GUILD, CHANNEL, GLOBAL)，用作谁和在哪可以触发此wait_for
        :param command_obj: 指定的Command，仅生效以下BotCommandObject的参数（command, regex, treat, at, short_circuit）
        :param timeout: 超时时间，单位秒，None为永远等待
        :return: Model.MESSAGE
        """
        self.__check_ready()
        data = TraceCallerData(TraceNames, ("args",))[0]
        command_obj.func = None
        scope_key = self.__session_manager.register_wait_for(data, scope, command_obj)
        _timeout_stamp = time() + timeout if timeout else None
        while True:
            check, result = self.__session_manager.check_wait_for(
                scope_key, command_obj
            )
            if not check:
                self.__session_manager.del_wait_for(data, command_obj)
                raise WaitError("找不到对应的wait_for()等待任务")
            if result is not None:
                break
            if _timeout_stamp and time() > _timeout_stamp:
                self.__session_manager.del_wait_for(data, command_obj)
                raise WaitTimeoutError(f"wait_for()等待超时： {command_obj}")
            sleep(0.5)
        return result

    # bot api
    def __check_ready(self):
        if not self._loop.is_running():
            raise RuntimeError(
                "Event loop is not running，请先通过BOT()实例的start()或block()方法启动bot并运行事件循环"
            )

    def security_setup(self, mini_id: str, mini_secret: str):
        self._api._mini_id = mini_id
        self._api._mini_secret = mini_secret

    def security_check(self, content: str) -> bool:
        """
        腾讯小程序侧内容安全检测接口，使用此接口必须填入bot_secret密钥

        :param content: 需要检测的内容
        :return: True或False（bool），代表是否通过安全检测
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.security_check(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    @staticmethod
    def get_bot_id():
        raise DeprecationWarning("SDK版本>=2.3.2后已遗弃get_bot_id()的api，改为BOT.robot.id")

    def get_bot_info(self) -> _api_model.get_bot_info():
        """
        获取机器人详情

        :return:返回的.data中为解析后的json数据
        """
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.get_bot_info(), self._loop)
        return future_.result(timeout=self._timeout)

    def get_bot_guilds(self) -> _api_model.get_bot_guilds():
        """
        获取机器人所在的所有频道列表

        :return: 返回的.data中为包含所有数据的一个list，列表每个项均为object数据
        """
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.get_bot_guilds(), self._loop)
        return future_.result(timeout=self._timeout)

    def get_guild_info(self, guild_id: str) -> _api_model.get_guild_info():
        """
        获取频道详情信息

        :param guild_id: 频道id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_guild_info(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def get_guild_channels(self, guild_id: str) -> _api_model.get_guild_channels():
        """
        获取频道的所有子频道列表数据

        :param guild_id: 频道id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_guild_channels(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def get_channels_info(self, channel_id: str) -> _api_model.get_channels_info():
        """
        获取子频道数据

        :param channel_id: 子频道id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_channels_info(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def create_channels(
        self,
        guild_id: str,
        name: str,
        type_: int,
        position: int,
        parent_id: str = None,
        sub_type: int = None,
        private_type: int = None,
        private_user_ids: List[str] = None,
        speak_permission: int = None,
        application_id: Optional[str] = None,
    ) -> _api_model.create_channels():
        """
        用于在 guild_id 指定的频道下创建一个子频道，一般仅私域机器人可用

        :param guild_id: 频道id
        :param name: 需要创建的子频道名
        :param type_: 需要创建的子频道类型
        :param position: 需要创建的子频道位置
        :param parent_id: 需要创建的子频道所属分组ID
        :param sub_type: 需要创建的子频道子类型
        :param private_type: 需要创建的子频道私密类型
        :param private_user_ids: 需要创建的子频道私密类型成员ID列表
        :param speak_permission: 需要创建的子频道发言权限
        :param application_id: 需要创建的应用类型子频道应用 AppID，仅应用子频道需要该字段
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.create_channels(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def patch_channels(
        self,
        channel_id: str,
        name: Optional[str] = None,
        position: Optional[int] = None,
        parent_id: Optional[str] = None,
        private_type: Optional[int] = None,
        speak_permission: Optional[int] = None,
    ) -> _api_model.patch_channels():
        """
        用于修改 channel_id 指定的子频道的信息，需要修改哪个字段，就传递哪个字段即可

        :param channel_id: 目标子频道ID
        :param name: 子频道名
        :param position: 子频道排序
        :param parent_id: 子频道所属分组id
        :param private_type: 子频道私密类型
        :param speak_permission: 子频道发言权限
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.patch_channels(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def delete_channels(self, channel_id) -> _api_model.delete_channels():
        """
        用于删除 channel_id 指定的子频道

        :param channel_id: 子频道id
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.delete_channels(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def get_online_nums(self, channel_id: str) -> _api_model.get_online_nums():
        """
        用于获取 channel_id 指定的音视频/直播子频道中在线人数

        :param channel_id: 子频道id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_online_nums(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def get_guild_members(self, guild_id: str) -> _api_model.get_guild_members():
        """
        用于获取 guild_id 指定的频道中所有成员的详情列表

        :param guild_id: 频道id
        :return: 返回的.data中为包含所有数据的一个list，列表每个项均为object数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_guild_members(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def get_role_members(
        self, guild_id: str, role_id: str
    ) -> _api_model.get_role_members():
        """
        用于获取 guild_id 频道中指定 role_id 身份组下所有成员的详情列表

        :param guild_id: 频道id
        :param role_id: 身份组id
        :return: 返回的.data中为包含所有数据的一个list，列表每个项均为object数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_role_members(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def get_member_info(
        self, guild_id: str, user_id: str
    ) -> _api_model.get_member_info():
        """
        用于获取 guild_id 指定的频道中 user_id 对应成员的详细信息

        :param guild_id: 频道id
        :param user_id: 成员id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_member_info(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def delete_member(
        self,
        guild_id: str,
        user_id: str,
        add_blacklist: bool = False,
        delete_history_msg_days: int = 0,
    ) -> _api_model.delete_member():
        """
        用于删除 guild_id 指定的频道下的成员 user_id

        :param guild_id: 频道ID
        :param user_id: 目标用户ID
        :param add_blacklist: 是否同时添加黑名单
        :param delete_history_msg_days: 用于撤回该成员的消息，可以指定撤回消息的时间范围
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.delete_member(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def get_guild_roles(self, guild_id: str) -> _api_model.get_guild_roles():
        """
        用于获取 guild_id指定的频道下的身份组列表

        :param guild_id: 频道id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_guild_roles(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def create_role(
        self,
        guild_id: str,
        name: Optional[str] = None,
        hoist: Optional[bool] = None,
        color: Optional[Union[str, Tuple[int, int, int]]] = None,
    ) -> _api_model.create_role():
        """
        用于在 guild_id 指定的频道下创建一个身份组

        :param guild_id: 频道id
        :param name: 身份组名（选填)
        :param hoist: 是否在成员列表中单独展示（选填）
        :param color: 身份组颜色，支持输入RGB的三位tuple或HEX的sting颜色（选填)
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.create_role(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def patch_role(
        self,
        guild_id: str,
        role_id: str,
        name: Optional[str] = None,
        hoist: Optional[bool] = None,
        color: Optional[Union[str, Tuple[int, int, int]]] = None,
    ) -> _api_model.patch_role():
        """
        用于修改频道 guild_id 下 role_id 指定的身份组

        :param guild_id: 频道id
        :param role_id: 需要修改的身份组ID
        :param name: 身份组名（选填)
        :param hoist: 是否在成员列表中单独展示（选填）
        :param color: 身份组颜色，支持输入RGB的三位tuple或HEX的sting颜色（选填)
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.patch_role(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def delete_role(self, guild_id: str, role_id: str) -> _api_model.delete_role():
        """
        用于删除频道 guild_id下 role_id 对应的身份组

        :param guild_id: 频道ID
        :param role_id: 需要删除的身份组ID
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.delete_role(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def create_role_member(
        self,
        user_id: str,
        guild_id: str,
        role_id: str,
        channel_id: Optional[str] = None,
    ) -> _api_model.role_members():
        """
        为频道指定成员添加指定身份组

        :param user_id: 目标用户的id
        :param guild_id: 目标频道guild id
        :param role_id: 身份组编号，可从例如get_roles函数获取
        :param channel_id: 如果要增加的身份组ID是5-子频道管理员，需要输入此项来指定具体是哪个子频道
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.create_role_member(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def delete_role_member(
        self,
        user_id: str,
        guild_id: str,
        role_id: str,
        channel_id: Optional[str] = None,
    ) -> _api_model.role_members():
        """
        删除频道指定成员的指定身份组

        :param user_id: 目标用户的id
        :param guild_id: 目标频道guild id
        :param role_id: 身份组编号，可从例如get_roles函数获取
        :param channel_id: 如果要增加的身份组ID是5-子频道管理员，需要输入此项来指定具体是哪个子频道
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.delete_role_member(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def get_channel_member_permission(
        self, channel_id: str, user_id: str
    ) -> _api_model.get_channel_member_permission():
        """
        用于获取 子频道 channel_id 下用户 user_id 的权限

        :param channel_id: 子频道id
        :param user_id: 用户id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_channel_member_permission(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def put_channel_member_permission(
        self,
        channel_id: str,
        user_id: str,
        add: Optional[str] = None,
        remove: Optional[str] = None,
    ) -> _api_model.put_channel_mr_permission():
        """
        用于修改子频道 channel_id 下用户 user_id 的权限

        :param channel_id: 子频道id
        :param user_id: 用户id
        :param add: 需要添加的权限，string格式，1，2，4，8按需进行位运算后的结果
        :param remove:需要删除的权限，string格式，1，2，4，8按需进行位运算后的结果
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.put_channel_member_permission(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def get_channel_role_permission(
        self, channel_id: str, role_id: str
    ) -> _api_model.get_channel_role_permission():
        """
        用于获取 子频道 channel_id 下身份组 role_id 的权限

        :param channel_id: 子频道id
        :param role_id: 身份组id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_channel_role_permission(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def put_channel_role_permission(
        self,
        channel_id: str,
        role_id: str,
        add: Optional[str] = None,
        remove: Optional[str] = None,
    ) -> _api_model.put_channel_mr_permission():
        """
        用于修改子频道 channel_id 下身份组 role_id 的权限

        :param channel_id: 子频道id
        :param role_id: 身份组id
        :param add: 需要添加的权限，string格式，1，2，4，8按需进行位运算后的结果
        :param remove:需要删除的权限，string格式，1，2，4，8按需进行位运算后的结果
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.put_channel_role_permission(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def get_message_info(
        self, channel_id: str, message_id: str
    ) -> _api_model.get_message_info():
        """
        用于获取子频道 channel_id 下的消息 message_id 的详情

        :param channel_id: 频道ID
        :param message_id: 目标消息ID
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_message_info(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def send_msg(
        self,
        channel_id: str,
        content: Optional[Union[str, BaseMessageApiModel]] = None,
        image: Optional[str] = None,
        file_image: Optional[Union[bytes, BinaryIO, str]] = None,
        message_id: Optional[str] = None,
        event_id: Optional[str] = None,
        message_reference_id: Optional[str] = None,
        ignore_message_reference_error: Optional[bool] = None,
    ) -> _api_model.send_msg():
        """
        发送普通消息的API

        :param channel_id: 子频道id
        :param content: 消息体【或消息文本（选填，此项与image至少需要有一个字段，否则无法下发消息）】
        :param image: 图片url，不可发送本地图片（选填，此项与msg至少需要有一个字段，否则无法下发消息）
        :param file_image: 本地图片，可选三种方式传参，具体可参阅github中的example_10或帮助文档
        :param message_id: 消息id（选填）
        :param event_id: 事件id（选填）
        :param message_reference_id: 引用消息的id（选填）
        :param ignore_message_reference_error: 是否忽略获取引用消息详情错误，默认否（选填）
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.send_msg(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def send_embed(
        self,
        channel_id: str,
        title: Optional[str] = None,
        content: Optional[List[str]] = None,
        image: Optional[str] = None,
        prompt: Optional[str] = None,
        message_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> _api_model.send_msg():
        """
        发送embed模板消息的API

        :param channel_id: 子频道id
        :param title: 标题文本（选填）
        :param content: 内容文本列表，每一项之间将存在分行（选填）
        :param image: 略缩图url，不可发送本地图片（选填）
        :param prompt: 消息弹窗通知的文本内容（选填）
        :param message_id: 消息id（选填）
        :param event_id: 事件id（选填）
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.send_embed(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def send_ark_23(
        self,
        channel_id: str,
        content: List[str],
        link: List[str],
        desc: Optional[str] = None,
        prompt: Optional[str] = None,
        message_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> _api_model.send_msg():
        """
        发送ark（id=23）模板消息的API，请注意机器人是否有权限使用此API

        :param channel_id: 子频道id
        :param content: 内容文本列表，每一项之间将存在分行
        :param link: 链接url列表，长度应与内容列一致。将根据位置顺序填充文本超链接，如文本不希望填充链接可使用空文本或None填充位置
        :param desc: 描述文本内容（选填）
        :param prompt: 消息弹窗通知的文本内容（选填）
        :param message_id: 消息id（选填）
        :param event_id: 事件id（选填）
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.send_ark_23(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def send_ark_24(
        self,
        channel_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        subtitile: Optional[str] = None,
        link: Optional[str] = None,
        image: Optional[str] = None,
        desc: Optional[str] = None,
        prompt: Optional[str] = None,
        message_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> _api_model.send_msg():
        """
        发送ark（id=24）模板消息的API，请注意机器人是否有权限使用此API

        :param channel_id: 子频道id
        :param title: 标题文本（选填）
        :param content: 详情描述文本（选填）
        :param subtitile: 子标题文本（选填）
        :param link: 跳转的链接url（选填）
        :param image: 略缩图url，不可发送本地图片（选填）
        :param desc: 描述文本内容（选填）
        :param prompt: 消息弹窗通知的文本内容（选填）
        :param message_id: 消息id（选填）
        :param event_id: 事件id（选填）
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.send_ark_24(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def send_ark_37(
        self,
        channel_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        link: Optional[str] = None,
        image: Optional[str] = None,
        prompt: Optional[str] = None,
        message_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> _api_model.send_msg():
        """
        发送ark（id=37）模板消息的API，请注意机器人是否有权限使用此API

        :param channel_id: 子频道id
        :param title: 标题文本（选填）
        :param content: 内容文本（选填）
        :param link: 跳转的链接url（选填）
        :param image: 略缩图url，不可发送本地图片（选填）
        :param prompt: 消息弹窗通知的文本内容（选填）
        :param message_id: 消息id（选填）
        :param event_id: 事件id（选填）
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.send_ark_37(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def send_markdown(
        self,
        channel_id: str,
        template_id: Optional[str] = None,
        key_values: Optional[
            Union[
                List[Dict[str, Union[str, List[str]]]], Dict[str, Union[str, List[str]]]
            ]
        ] = None,
        content: Optional[str] = None,
        keyboard_id: Optional[str] = None,
        keyboard_content: Optional[Dict] = None,
        message_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> _api_model.send_msg():
        """
        发送markdown消息的API，请注意机器人是否有权限使用此API

        :param channel_id: 子频道id
        :param template_id: markdown 模板 id（选填，与content不可同时存在）
        :param key_values: markdown 模版 key values列表，格式为：{key1: value1, key2: value2}（选填，与content不可同时存在）
        :param content: 原生 markdown 内容（选填，与template_id, key, values不可同时存在）
        :param keyboard_id: keyboard 模板 id（选填，与keyboard_content不可同时存在）
        :param keyboard_content: 原生 keyboard 内容（选填，与keyboard_id不可同时存在）
        :param message_id: 消息id（选填）
        :param event_id: 事件id（选填）
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.send_markdown(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def delete_msg(
        self, channel_id: str, message_id: str, hidetip: bool = False
    ) -> _api_model.delete_msg():
        """
        撤回消息的API，注意一般情况下仅私域可以使用

        :param channel_id: 子频道id
        :param message_id: 需撤回消息的消息id
        :param hidetip: 是否隐藏提示小灰条，True为隐藏，False为显示（选填）
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.delete_msg(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def get_guild_setting(self, guild_id: str) -> _api_model.get_guild_setting():
        """
        用于获取机器人在频道 guild_id 内的消息频率设置

        :param guild_id: 频道id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_guild_setting(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def create_dm_guild(
        self, target_id: str, guild_id: str
    ) -> _api_model.create_dm_guild():
        """
        当机器人主动跟用户私信时，创建并获取一个虚拟频道id的API

        :param target_id: 目标用户id
        :param guild_id: 机器人跟目标用户所在的频道id
        :return: 返回的.data中为解析后的json数据，注意发送私信仅需要使用guild_id这一项虚拟频道id的数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.create_dm_guild(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def send_dm(
        self,
        guild_id: str,
        content: Optional[Union[str, BaseMessageApiModel]] = None,
        image: Optional[str] = None,
        file_image: Optional[Union[bytes, BinaryIO, str]] = None,
        message_id: Optional[str] = None,
        event_id: Optional[str] = None,
        message_reference_id: Optional[str] = None,
        ignore_message_reference_error: Optional[bool] = None,
    ) -> _api_model.send_msg():
        """
        私信用户的API

        :param guild_id: 虚拟频道id（非子频道id），从用户主动私信机器人的事件、或机器人主动创建私信的API中获取
        :param content: 消息体【或消息文本（选填，此项与image至少需要有一个字段，否则无法下发消息）】
        :param image: 图片url，不可发送本地图片（选填，此项与msg至少需要有一个字段，否则无法下发消息）
        :param file_image: 本地图片，可选三种方式传参，具体可参阅github中的example_10或帮助文档
        :param message_id: 消息id（选填）
        :param event_id: 事件id（选填）
        :param message_reference_id: 引用消息的id（选填）
        :param ignore_message_reference_error: 是否忽略获取引用消息详情错误，默认否（选填）
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.send_dm(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def delete_dm_msg(
        self, guild_id: str, message_id: str, hidetip: bool = False
    ) -> _api_model.delete_msg():
        """
        用于撤回私信频道 guild_id 中 message_id 指定的私信消息。只能用于撤回机器人自己发送的私信

        :param guild_id: 虚拟频道id（非子频道id），从用户主动私信机器人的事件、或机器人主动创建私信的API中获取
        :param message_id: 需撤回消息的消息id
        :param hidetip: 是否隐藏提示小灰条，True为隐藏，False为显示（选填）
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.delete_dm_msg(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def mute_all_member(
        self,
        guild_id: str,
        mute_end_timestamp: Optional[str] = None,
        mute_seconds: Optional[str] = None,
    ) -> _api_model.mute_member():
        """
        用于将频道的全体成员（非管理员）禁言

        :param guild_id: 频道id
        :param mute_end_timestamp: 禁言到期时间戳，绝对时间戳，单位：秒（与 mute_seconds 字段同时赋值的话，以该字段为准）
        :param mute_seconds: 禁言多少秒（两个字段二选一，默认以 mute_end_timestamp 为准）
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.mute_all_member(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def mute_member(
        self,
        guild_id: str,
        user_id: str,
        mute_end_timestamp: Optional[str] = None,
        mute_seconds: Optional[str] = None,
    ) -> _api_model.mute_member():
        """
        用于禁言频道 guild_id 下的成员 user_id

        :param guild_id: 频道id
        :param user_id: 目标成员的用户ID
        :param mute_end_timestamp: 禁言到期时间戳，绝对时间戳，单位：秒（与 mute_seconds 字段同时赋值的话，以该字段为准）
        :param mute_seconds: 禁言多少秒（两个字段二选一，默认以 mute_end_timestamp 为准）
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.mute_member(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def mute_members(
        self,
        guild_id: str,
        user_id: List[str],
        mute_end_timestamp: Optional[str] = None,
        mute_seconds: Optional[str] = None,
    ) -> _api_model.mute_members():
        """
        用于将频道的指定批量成员（非管理员）禁言

        :param guild_id: 频道id
        :param user_id: 目标成员的用户ID列表
        :param mute_end_timestamp: 禁言到期时间戳，绝对时间戳，单位：秒（与 mute_seconds 字段同时赋值的话，以该字段为准）
        :param mute_seconds: 禁言多少秒（两个字段二选一，默认以 mute_end_timestamp 为准）
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.mute_members(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def create_announce(
        self,
        guild_id: str,
        channel_id: Optional[str] = None,
        message_id: Optional[str] = None,
        announces_type: Optional[int] = None,
        recommend_channels: Optional[List[model.AnnounceRecommendChannels]] = None,
        recommend_channels_id: Optional[List[str]] = None,
        recommend_channels_introduce: Optional[List[str]] = None,
    ) -> _api_model.create_announce():
        """
        用于创建频道全局公告，公告类型分为 消息类型的频道公告 和 推荐子频道类型的频道公告

        :param guild_id: 频道id
        :param channel_id: 子频道id，message_id 有值则为必填
        :param message_id: 消息id，此项有值则优选将某条消息设置为成员公告
        :param announces_type: 公告类别 0：成员公告，1：欢迎公告，默认为成员公告
        :param recommend_channels: 推荐子频道id与推荐语的dict列表，会一次全部替换推荐子频道列表
        :param recommend_channels_id: deprecated
        :param recommend_channels_introduce: deprecated
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.create_announce(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def delete_announce(
        self, guild_id: str, message_id: str = "all"
    ) -> _api_model.delete_announce():
        """
        用于删除频道 guild_id 下指定 message_id 的全局公告

        :param guild_id: 频道id
        :param message_id: message_id有值时会校验message_id合法性；若不校验，请将message_id设置为all（默认为all）
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.delete_announce(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def create_pinmsg(self, channel_id: str, message_id: str) -> _api_model.pinmsg():
        """
        用于添加子频道 channel_id 内的精华消息

        :param channel_id: 子频道id
        :param message_id: 目标消息id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.create_pinmsg(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def delete_pinmsg(
        self, channel_id: str, message_id: str
    ) -> _api_model.delete_pinmsg():
        """
        用于删除子频道 channel_id 下指定 message_id 的精华消息

        :param channel_id: 子频道id
        :param message_id: 目标消息id
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.delete_pinmsg(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def get_pinmsg(self, channel_id: str) -> _api_model.pinmsg():
        """
        用于获取子频道 channel_id 内的精华消息

        :param channel_id: 子频道id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.get_pinmsg(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def get_schedules(
        self, channel_id: str, since: Optional[int] = None
    ) -> _api_model.get_schedules():
        """
        用于获取channel_id指定的子频道中当天的日程列表

        :param channel_id: 日程子频道id
        :param since: 起始时间戳(ms)
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.get_schedules(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def get_schedule_info(
        self, channel_id: str, schedule_id: str
    ) -> _api_model.schedule_info():
        """
        获取日程子频道 channel_id 下 schedule_id 指定的的日程的详情

        :param channel_id: 日程子频道id
        :param schedule_id: 日程id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_schedule_info(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def create_schedule(
        self,
        channel_id: str,
        schedule_name: str,
        start_timestamp: str,
        end_timestamp: str,
        jump_channel_id: str,
        remind_type: str,
    ) -> _api_model.schedule_info():
        """
        用于在 channel_id 指定的日程子频道下创建一个日程

        :param channel_id: 日程子频道id
        :param schedule_name: 日程名称
        :param start_timestamp: 日程开始时间戳(ms)
        :param end_timestamp: 日程结束时间戳(ms)
        :param jump_channel_id: 日程开始时跳转到的子频道id
        :param remind_type: 日程提醒类型
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.create_schedule(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def patch_schedule(
        self,
        channel_id: str,
        schedule_id: str,
        schedule_name: str,
        start_timestamp: str,
        end_timestamp: str,
        jump_channel_id: str,
        remind_type: str,
    ) -> _api_model.schedule_info():
        """
        用于修改日程子频道 channel_id 下 schedule_id 指定的日程的详情

        :param channel_id: 日程子频道id
        :param schedule_id: 日程id
        :param schedule_name: 日程名称
        :param start_timestamp: 日程开始时间戳(ms)
        :param end_timestamp: 日程结束时间戳(ms)
        :param jump_channel_id: 日程开始时跳转到的子频道id
        :param remind_type: 日程提醒类型
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.patch_schedule(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def delete_schedule(
        self, channel_id: str, schedule_id: str
    ) -> _api_model.delete_schedule():
        """
        用于删除日程子频道 channel_id 下 schedule_id 指定的日程

        :param channel_id: 日程子频道id
        :param schedule_id: 日程id
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.delete_schedule(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def create_reaction(
        self, channel_id: str, message_id: str, type_: str, id_: str
    ) -> _api_model.reactions():
        """
        对message_id指定的消息进行表情表态

        :param channel_id: 子频道id
        :param message_id: 目标消息id
        :param type_: 表情类型
        :param id_: 表情id
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.create_reaction(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def delete_reaction(
        self, channel_id: str, message_id: str, type_: str, id_: str
    ) -> _api_model.reactions():
        """
        删除自己对message_id指定消息的表情表态

        :param channel_id: 子频道id
        :param message_id: 目标消息id
        :param type_: 表情类型
        :param id_: 表情id
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.delete_reaction(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def get_reaction_users(
        self, channel_id: str, message_id: str, type_: str, id_: str
    ) -> _api_model.get_reaction_users():
        """
        拉取对消息 message_id 指定表情表态的用户列表

        :param channel_id: 子频道id
        :param message_id: 目标消息id
        :param type_: 表情类型
        :param id_: 表情id
        :return: 返回的.data中为解析后的json数据列表
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_reaction_users(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def control_audio(
        self,
        channel_id: str,
        status: int,
        audio_url: Optional[str] = None,
        text: Optional[str] = None,
    ) -> _api_model.audio():
        """
        用于控制子频道 channel_id 下的音频

        :param channel_id: 子频道id
        :param status: 播放状态
        :param audio_url: 音频数据的url，可选，status为0时传
        :param text: 状态文本（比如：简单爱-周杰伦），可选，status为0时传，其他操作不传
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.control_audio(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def bot_on_mic(self, channel_id: str) -> _api_model.audio():
        """
        机器人在 channel_id 对应的语音子频道上麦

        :param channel_id: 子频道id
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.bot_on_mic(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def bot_off_mic(self, channel_id: str) -> _api_model.audio():
        """
        机器人在 channel_id 对应的语音子频道下麦

        :param channel_id: 子频道id
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.bot_off_mic(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def get_threads(self, channel_id: str) -> _api_model.get_threads():
        """
        获取子频道下的帖子列表

        :param channel_id: 目标论坛子频道id
        :return: 返回的.data中为解析后的json数据列表
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.get_threads(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def get_thread_info(
        self, channel_id: str, thread_id: str
    ) -> _api_model.get_thread_info():
        """
        获取子频道下的帖子详情

        :param channel_id: 目标论坛子频道id
        :param thread_id: 帖子id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_thread_info(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def create_thread(
        self, channel_id: str, title: str, content: Union[str, Dict], format_: int
    ) -> _api_model.create_thread():
        """
        创建帖子，创建成功后，返回创建成功的任务ID

        :param channel_id: 目标论坛子频道id
        :param title: 帖子标题
        :param content: 帖子内容（具体格式根据format_判断）
        :param format_: 帖子文本格式（1：普通文本、2：HTML、3：Markdown、4：Json）
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.create_thread(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def delete_thread(
        self, channel_id: str, thread_id: str
    ) -> _api_model.delete_thread():
        """
        删除指定子频道下的某个帖子

        :param channel_id: 目标论坛子频道id
        :param thread_id: 帖子id
        :return: 返回的.result显示是否成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(self._api.delete_thread(**_args), self._loop)
        return future_.result(timeout=self._timeout)

    def get_guild_permissions(
        self, guild_id: str
    ) -> _api_model.get_guild_permissions():
        """
        获取机器人在频道 guild_id 内可以使用的权限列表

        :param guild_id: 频道id
        :return: 返回的.data中为解析后的json数据
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.get_guild_permissions(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)

    def create_permission_demand(
        self, guild_id: str, channel_id: str, api: str, desc: Optional[str]
    ) -> _api_model.create_permission_demand():
        """
        发送频道API接口权限授权链接到频道

        :param guild_id: 频道id
        :param channel_id: 子频道id
        :param api: 需求权限的API在sdk的名字
        :param desc: 机器人申请对应的API接口权限后可以使用功能的描述
        :return: 返回成功或不成功
        """
        _args = locals()
        _args.pop("self")
        self.__check_ready()
        future_ = run_coroutine_threadsafe(
            self._api.create_permission_demand(**_args), self._loop
        )
        return future_.result(timeout=self._timeout)
