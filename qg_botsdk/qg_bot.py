# !/usr/bin/env python3
# encoding: utf-8
from os import getpid, PathLike
from os.path import exists
from asyncio import get_event_loop, sleep
from json import loads
from json.decoder import JSONDecodeError
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from time import time
from threading import Thread
from typing import Any, Callable, Optional, Union, BinaryIO
from io import BufferedReader
from .logger import Logger
from .model import Model
from ._api_model import api_converter, api_converter_re, ReplyModel
from .qg_bot_ws import BotWs
from .utils import objectize, convert_color, exception_handler, http_temp, regular_temp, empty_temp, sdk_error_temp

reply_model = ReplyModel()
retry = Retry(total=4, connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
security_header = {'Content-Type': 'application/json', 'charset': 'UTF-8'}
version = '2.1.5'
pid = getpid()
pid = getpid()
print(f'本次程序进程ID：{pid} | SDK版本：{version} | 即将开始运行机器人……')


class BOT:

    def __init__(self, bot_id: str, bot_token: str, bot_secret: str = None, is_private: bool = False,
                 is_sandbox: bool = False, max_shard: int = 5, no_permission_warning: bool = True):
        """
        机器人主体，输入BotAppID和密钥，并绑定函数后即可快速使用

        :param bot_id: 机器人平台后台BotAppID（开发者ID）项，必填
        :param bot_token: 机器人平台后台机器人令牌项，必填
        :param bot_secret: 机器人平台后台机器人密钥项，如需要使用安全检测功能需填写此项
        :param is_private: 机器人是否为私域机器人，默认False
        :param is_sandbox: 是否开启沙箱环境，默认False
        :param max_shard: 最大分片数，请根据配置自行判断，默认5
        :param no_permission_warning: 是否开启当机器人获取疑似权限不足的事件时的警告提示，默认开启
        """
        self.logger = Logger(bot_id)
        self.bot_id = bot_id
        self.bot_token = bot_token
        self.bot_secret = bot_secret
        self.is_private = is_private
        if is_sandbox:
            self.bot_url = r'https://sandbox.api.sgroup.qq.com'
        else:
            self.bot_url = r'https://api.sgroup.qq.com'
        if not self.bot_id or not self.bot_token:
            raise type('IdTokenMissing', (Exception,), {})(
                '你还没有输入 bot_id 和 bot_token，无法连接使用机器人\n如尚未有相关票据，'
                '请参阅 https://thoughts.teambition.com/share/627533408adeb10041b935b1#title=快速入门 了解相关详情')
        self.intents = 0
        self.max_shard = max_shard
        self.__on_delete_function = None
        self.__on_msg_function = None
        self.__on_dm_function = None
        self.__on_guild_event_function = None
        self.__on_guild_member_function = None
        self.__on_reaction_function = None
        self.__on_interaction_function = None
        self.__on_audit_function = None
        self.__on_forum_function = None
        self.__on_audio_function = None
        self.__repeat_function = None
        self.__on_start_function = None
        self.is_filter_self = True
        self.check_interval = 10
        self.running = False
        self.__session = Session()
        self.__session.headers = {'Authorization': "Bot " + str(self.bot_id) + "." + str(self.bot_token)}
        self.__session.keep_alive = False
        self.__session.mount('http://', adapter)
        self.__session.mount('https://', adapter)
        self.__bot_classes = []
        self.__bot_threads = []
        self.__main_loop = get_event_loop()
        self.msg_treat = False
        self.dm_treat = False
        self.security_code = ''
        self.code_expire = 0
        self.no_permission_warning = no_permission_warning

    async def __time_event_check(self):
        while self.running:
            try:
                self.__repeat_function()
            except Exception as error:
                self.logger.error(error)
                self.logger.debug(exception_handler(error))
            await sleep(self.check_interval)

    def bind_msg(self, on_msg_function: Callable[[Model.MESSAGE], Any], treated_data: bool = True):
        """
        用作绑定接收消息的函数，将根据机器人是否公域自动判断接收艾特或所有消息

        :param on_msg_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        :param treated_data: 是否返回经转义处理的文本，如是则会在返回的Object中添加一个treated_msg的子类，默认True
        """
        self.__on_msg_function = on_msg_function
        if treated_data:
            self.msg_treat = True
        if not self.is_private:
            self.intents = self.intents | 1 << 30
            self.logger.info('消息（所有消息）接收函数订阅成功')
        else:
            self.intents = self.intents | 1 << 9
            self.logger.info('消息（艾特消息）接收函数订阅成功')

    def bind_dm(self, on_dm_function: Callable[[Model.DIRECT_MESSAGE], Any], treated_data: bool = True):
        """
        用作绑定接收私信消息的函数

        :param on_dm_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        :param treated_data: 是否返回经转义处理的文本，如是则会在返回的Object中添加一个treated_msg的子类，默认True
        """
        self.__on_dm_function = on_dm_function
        self.intents = self.intents | 1 << 12
        if treated_data:
            self.dm_treat = True
        self.logger.info('私信接收函数订阅成功')

    def bind_msg_delete(self, on_delete_function: Callable[[Model.MESSAGE_DELETE], Any], is_filter_self: bool = True):
        """
        用作绑定接收消息撤回事件的函数，注册时将自动根据公域私域注册艾特或全部消息，但不会主动注册私信事件

        :param on_delete_function:类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        :param is_filter_self: 是否过滤用户自行撤回的消息，只接受管理撤回事件
        """
        self.__on_delete_function = on_delete_function
        self.is_filter_self = is_filter_self
        if self.is_private:
            self.intents = self.intents | 1 << 30
        else:
            self.intents = self.intents | 1 << 9
        self.logger.info('撤回事件订阅成功')

    def bind_guild_event(self, on_guild_event_function: Callable[[Model.GUILDS], Any]):
        """
        用作绑定接收频道信息的函数

        :param on_guild_event_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.__on_guild_event_function = on_guild_event_function
        self.intents = self.intents | 1 << 0
        self.logger.info('频道事件订阅成功')

    def bind_guild_member(self, on_guild_member_function: Callable[[Model.GUILD_MEMBERS], Any]):
        """
        用作绑定接收频道成员信息的函数

        :param on_guild_member_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.__on_guild_member_function = on_guild_member_function
        self.intents = self.intents | 1 << 1
        self.logger.info('频道成员事件订阅成功')

    def bind_reaction(self, on_reaction_function: Callable[[Model.REACTION], Any]):
        """
        用作绑定接收表情表态信息的函数

        :param on_reaction_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.__on_reaction_function = on_reaction_function
        self.intents = self.intents | 1 << 10
        self.logger.info('表情表态事件订阅成功')

    def bind_interaction(self, on_interaction_function: Callable[[Any], Any]):
        """
        用作绑定接收互动事件的函数，当前未有录入数据结构

        :param on_interaction_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.__on_interaction_function = on_interaction_function
        self.intents = self.intents | 1 << 26
        self.logger.info('互动事件订阅成功')

    def bind_audit(self, on_audit_function: Callable[[Model.MESSAGE_AUDIT], Any]):
        """
        用作绑定接收审核事件的函数

        :param on_audit_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.__on_audit_function = on_audit_function
        self.intents = self.intents | 1 << 27
        self.logger.info('审核事件订阅成功')

    def bind_forum(self, on_forum_function: Callable[[Model.FORUMS_EVENT], Any]):
        """
        用作绑定接收论坛事件的函数，一般仅私域机器人能注册此事件

        .. note::
            当前仅可以接收FORUM_THREAD_CREATE、FORUM_THREAD_UPDATE、FORUM_THREAD_DELETE三个事件

        :param on_forum_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """

        self.__on_forum_function = on_forum_function
        self.intents = self.intents | 1 << 28
        self.logger.info('论坛事件订阅成功')
        if not self.is_private and self.no_permission_warning:
            self.logger.warning('请注意，一般公域机器人并不能注册论坛事件，请检查自身是否拥有相关权限')

    def bind_audio(self, on_audio_function: Callable[[Model.AUDIO_ACTION], Any]):
        """
        用作绑定接收论坛事件的函数

        :param on_audio_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.__on_audio_function = on_audio_function
        self.intents = self.intents | 1 << 29
        self.logger.info('音频事件订阅成功')
        if self.no_permission_warning:
            self.logger.warning('请注意，一般机器人并不能注册音频事件（需先进行申请），请检查自身是否拥有相关权限（如已申请可忽略此消息）')

    def register_repeat_event(self, time_function: Callable[[], Any], check_interval: float or int = 10):
        """
        用作注册重复事件的函数，注册并开始机器人后，会根据间隔时间不断调用注册的函数

        :param time_function: 类型为function，该函数不应包含任何参数
        :param check_interval: 每多少秒检查调用一次时间事件函数，默认10
        """
        self.__repeat_function = time_function
        self.check_interval = check_interval
        self.logger.info('重复运行事件注册成功')

    def register_start_event(self, on_start_function: Callable[[], Any]):
        """
        用作注册机器人开始时运行的函数，此函数不应有无限重复的内容

        :param on_start_function: 类型为function，该函数不应包含任何参数
        """
        self.__on_start_function = on_start_function
        self.logger.info('初始事件注册成功')

    def __security_check_code(self):
        if self.bot_secret is None:
            self.logger.error('无法调用内容安全检测接口（备注：没有填入机器人密钥）')
            return None
        code = self.__session.get(f'https://api.q.qq.com/api/getToken?grant_type=client_credential&appid={self.bot_id}&'
                                  f'secret={self.bot_secret}').json()
        try:
            self.security_code = code['access_token']
            self.code_expire = time() + 7000
            return self.security_code
        except KeyError:
            self.logger.error('无法调用内容安全检测接口（备注：请检查机器人密钥是否正确）')
            return None

    def security_check(self, content: str) -> bool:
        """
        腾讯小程序侧内容安全检测接口，使用此接口必须填入bot_secret密钥

        :param content: 需要检测的内容
        :return: True或False（bool），代表是否通过安全检测
        """
        if not self.security_code or time() >= self.code_expire:
            self.__security_check_code()
        check = self.__session.post(
            f'https://api.q.qq.com/api/json/security/MsgSecCheck?access_token={self.security_code}',
            headers=security_header, json={'content': content}).json()
        self.logger.debug(check)
        if check['errCode'] in (-1800110107, -1800110108):
            self.__security_check_code()
            check = self.__session.post(f'https://api.q.qq.com/api/json/security/MsgSecCheck?'
                                        f'access_token={self.security_code}', headers=security_header,
                                        json={'content': content}).json()
            self.logger.debug(check)
        if check['errCode'] == 0:
            return True
        return False

    def check_warning(self, name: str):
        if not self.is_private and self.no_permission_warning:
            self.logger.warning(f'请注意，一般公域机器人并不能使用{name}API，请检查自身是否拥有相关权限')

    def get_bot_id(self) -> reply_model.get_bot_id():
        """
        获取机器人在频道场景的用户ID

        :return: 返回的.data中为机器人用户ID，如未注册则返回None
        """
        try:
            return objectize({'data': self.__bot_classes[0].bot_qid, 'result': True})
        except IndexError:
            return objectize({'data': None, 'result': False})

    def get_bot_info(self) -> reply_model.get_bot_info():
        """
        获取机器人详情

        :return:返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(f'{self.bot_url}/users/@me')
        return regular_temp(return_)

    def get_bot_guilds(self) -> reply_model.get_bot_guilds():
        """
        获取机器人所在的所有频道列表

        :return: 返回的.data中为包含所有数据的一个list，列表每个项均为object数据
        """
        trace_ids = []
        results = []
        data = []
        return_dict = None
        try:
            while True:
                if return_dict is None:
                    return_ = self.__session.get(f'{self.bot_url}/users/@me/guilds')
                elif len(return_dict) == 100:
                    return_ = self.__session.get(f'{self.bot_url}/users/@me/guilds?after=' + return_dict[-1]['id'])
                else:
                    break
                trace_ids.append(return_.headers['X-Tps-Trace-Id'])
                return_dict = return_.json()
                if isinstance(return_dict, dict) and 'code' in return_dict.keys():
                    results.append(False)
                    data.append(return_dict)
                    break
                else:
                    results.append(True)
                    for items in return_dict:
                        data.append(items)
        except JSONDecodeError:
            return objectize({'data': [], 'trace_id': trace_ids, 'result': False})
        return objectize({'data': data, 'trace_id': trace_ids, 'result': results})

    def get_guild_info(self, guild_id: str) -> reply_model.get_guild_info():
        """
        获取频道详情信息

        :param guild_id: 频道id
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(f'{self.bot_url}/guilds/{guild_id}')
        return regular_temp(return_)

    def get_guild_channels(self, guild_id: str) -> reply_model.get_guild_channels():
        """
        获取频道的所有子频道列表数据

        :param guild_id: 频道id
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(f'{self.bot_url}/guilds/{guild_id}/channels')
        return regular_temp(return_)

    def get_channels_info(self, channel_id: str) -> reply_model.get_channels_info():
        """
        获取子频道数据

        :param channel_id: 子频道id
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(f'{self.bot_url}/channels/{channel_id}')
        return regular_temp(return_)

    def create_channels(self, guild_id: str, name: str, type_: int, position: int, parent_id: str, sub_type: int,
                        private_type: int, private_user_ids: list[str], speak_permission: int,
                        application_id: Optional[str] = None) -> reply_model.create_channels():
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
        self.check_warning('创建子频道')
        json_ = {"name": name, "type": type_, "position": position, "parent_id": parent_id, "sub_type": sub_type,
                 "private_type": private_type, "private_user_ids": private_user_ids,
                 "speak_permission": speak_permission, "application_id": application_id}
        return_ = self.__session.post(f'{self.bot_url}/guilds/{guild_id}/channels', json=json_)
        return regular_temp(return_)

    def patch_channels(self, channel_id: str, name: Optional[str] = None, position: Optional[int] = None,
                       parent_id: Optional[str] = None, private_type: Optional[int] = None,
                       speak_permission: Optional[int] = None) -> reply_model.patch_channels():
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
        self.check_warning('修改子频道')
        json_ = {"name": name, "position": position, "parent_id": parent_id, "private_type": private_type,
                 "speak_permission": speak_permission}
        return_ = self.__session.patch(f'{self.bot_url}/channels/{channel_id}', json=json_)
        return regular_temp(return_)

    def delete_channels(self, channel_id) -> reply_model.delete_channels():
        """
        用于删除 channel_id 指定的子频道

        :param channel_id: 子频道id
        :return: 返回的.result显示是否成功
        """
        self.check_warning('删除子频道')
        return_ = self.__session.delete(f'{self.bot_url}/channels/{channel_id}')
        return http_temp(return_, 200)

    def get_guild_members(self, guild_id: str) -> reply_model.get_guild_members():
        """
        用于获取 guild_id 指定的频道中所有成员的详情列表

        :param guild_id: 频道id
        :return: 返回的.data中为包含所有数据的一个list，列表每个项均为object数据
        """
        return_ = self.__session.get(f'{self.bot_url}/guilds/{guild_id}/members?limit=400')
        trace_ids = [return_.headers['X-Tps-Trace-Id']]
        results = []
        data = []
        try:
            return_dict = return_.json()
            if isinstance(return_dict, dict) and 'code' in return_dict.keys():
                results.append(False)
                return objectize({'data': [return_dict], 'trace_id': trace_ids, 'result': results})
            else:
                results.append(True)
                for items in return_dict:
                    data.append(items)
            while True:
                if len(return_dict) == 400:
                    return_ = self.__session.get(f'{self.bot_url}/guilds/{guild_id}/members?limit=400&after=' +
                                                 return_dict[-1]['user']['id'])
                    trace_ids.append(return_.headers['X-Tps-Trace-Id'])
                    return_dict = return_.json()
                    if isinstance(return_dict, dict) and 'code' in return_dict.keys():
                        results.append(False)
                    else:
                        results.append(True)
                        for items in return_dict:
                            if items not in data:
                                data.append(items)
                else:
                    break
        except JSONDecodeError:
            return objectize({'data': [], 'trace_id': trace_ids, 'result': [False]})
        if data:
            return objectize({'data': data, 'trace_id': trace_ids, 'result': results})
        else:
            return objectize({'data': [], 'trace_id': trace_ids, 'result': [False]})

    def get_member_info(self, guild_id: str, user_id: str) -> reply_model.get_member_info():
        """
        用于获取 guild_id 指定的频道中 user_id 对应成员的详细信息

        :param guild_id: 频道id
        :param user_id: 成员id
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(f'{self.bot_url}/guilds/{guild_id}/members/{user_id}')
        return regular_temp(return_)

    def delete_member(self, guild_id: str, user_id: str, add_blacklist: bool = False,
                      delete_history_msg_days: int = 0) -> reply_model.delete_member():
        """
        用于删除 guild_id 指定的频道下的成员 user_id

        :param guild_id: 频道ID
        :param user_id: 目标用户ID
        :param add_blacklist: 是否同时添加黑名单
        :param delete_history_msg_days: 用于撤回该成员的消息，可以指定撤回消息的时间范围
        :return: 返回的.result显示是否成功
        """
        self.check_warning('删除频道成员')
        if delete_history_msg_days not in (3, 7, 15, 30, 0, -1):
            return sdk_error_temp('注意delete_history_msg_days的数值只能是3，7，15，30，0，-1')
        json_ = {'add_blacklist': add_blacklist, 'delete_history_msg_days': delete_history_msg_days}
        return_ = self.__session.delete(f'{self.bot_url}/guilds/{guild_id}/members/{user_id}', json=json_)
        return http_temp(return_, 204)

    def get_guild_roles(self, guild_id: str) -> reply_model.get_guild_roles():
        """
        用于获取 guild_id指定的频道下的身份组列表

        :param guild_id: 频道id
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(f'{self.bot_url}/guilds/{guild_id}/roles')
        return regular_temp(return_)

    def create_role(self, guild_id: str, name: Optional[str] = None, hoist: Optional[bool] = None,
                    color: Optional[Union[str, tuple[int, int, int]]] = None) -> reply_model.create_role():
        """
        用于在 guild_id 指定的频道下创建一个身份组

        :param guild_id: 频道id
        :param name: 身份组名（选填)
        :param hoist: 是否在成员列表中单独展示（选填）
        :param color: 身份组颜色，支持输入RGB的三位tuple或HEX的sting颜色（选填)
        :return: 返回的.data中为解析后的json数据
        """
        if hoist is not None:
            if hoist:
                hoist_ = 1
            else:
                hoist_ = 0
        else:
            hoist_ = None
        if color is not None:
            color_ = convert_color(color)
        else:
            color_ = None
        json_ = {'name': name, 'color': color_, 'hoist': hoist_}
        return_ = self.__session.post(f'{self.bot_url}/guilds/{guild_id}/roles', json=json_)
        return regular_temp(return_)

    def patch_role(self, guild_id: str, role_id: str, name: Optional[str] = None, hoist: Optional[bool] = None,
                   color: Optional[Union[str, tuple[int, int, int]]] = None) -> reply_model.patch_role():
        """
        用于修改频道 guild_id 下 role_id 指定的身份组

        :param guild_id: 频道id
        :param role_id: 需要修改的身份组ID
        :param name: 身份组名（选填)
        :param hoist: 是否在成员列表中单独展示（选填）
        :param color: 身份组颜色，支持输入RGB的三位tuple或HEX的sting颜色（选填)
        :return: 返回的.data中为解析后的json数据
        """
        if hoist is not None:
            if hoist:
                hoist_ = 1
            else:
                hoist_ = 0
        else:
            hoist_ = None
        if color is not None:
            color_ = convert_color(color)
        else:
            color_ = None
        json_ = {'name': name, 'color': color_, 'hoist': hoist_}
        return_ = self.__session.patch(f'{self.bot_url}/guilds/{guild_id}/roles/{role_id}', json=json_)
        return regular_temp(return_)

    def delete_role(self, guild_id: str, role_id: str) -> reply_model.delete_role():
        """
        用于删除频道 guild_id下 role_id 对应的身份组

        :param guild_id: 频道ID
        :param role_id: 需要删除的身份组ID
        :return: 返回的.result显示是否成功
        """
        return_ = self.__session.delete(f'{self.bot_url}/guilds/{guild_id}/roles/{role_id}')
        return http_temp(return_, 204)

    def create_role_member(self, user_id: str, guild_id: str, role_id: str,
                           channel_id: Optional[str] = None) -> reply_model.role_members():
        """
        为频道指定成员添加指定身份组

        :param user_id: 目标用户的id
        :param guild_id: 目标频道guild id
        :param role_id: 身份组编号，可从例如get_roles函数获取
        :param channel_id: 如果要增加的身份组ID是5-子频道管理员，需要输入此项来指定具体是哪个子频道
        :return: 返回的.result显示是否成功
        """
        if role_id == '5':
            if channel_id is not None:
                return_ = self.__session.put(f'{self.bot_url}/guilds/{guild_id}/members/{user_id}/roles/{role_id}',
                                             json={"channel": {"id": channel_id}})
            else:
                return sdk_error_temp('注意如果要增加的身份组ID是5-子频道管理员，需要输入channel_id项来指定具体是哪个子频道')
        else:
            return_ = self.__session.put(f'{self.bot_url}/guilds/{guild_id}/members/{user_id}/roles/{role_id}')
        return http_temp(return_, 204)

    def delete_role_member(self, user_id: str, guild_id: str, role_id: str,
                           channel_id: Optional[str] = None) -> reply_model.role_members():
        """
        删除频道指定成员的指定身份组

        :param user_id: 目标用户的id
        :param guild_id: 目标频道guild id
        :param role_id: 身份组编号，可从例如get_roles函数获取
        :param channel_id: 如果要增加的身份组ID是5-子频道管理员，需要输入此项来指定具体是哪个子频道
        :return: 返回的.result显示是否成功
        """
        if role_id == '5':
            if channel_id is not None:
                return_ = self.__session.delete(f'{self.bot_url}/guilds/{guild_id}/members/{user_id}/roles/'
                                                f'{role_id}', json={"channel": {"id": channel_id}})
            else:
                return sdk_error_temp('注意如果要增加的身份组ID是5-子频道管理员，需要输入channel_id项来指定具体是哪个子频道')
        else:
            return_ = self.__session.delete(f'{self.bot_url}/guilds/{guild_id}/members/{user_id}/roles/{role_id}')
        return http_temp(return_, 204)

    def get_channel_member_permission(self, channel_id: str, user_id: str) -> \
            reply_model.get_channel_member_permission():
        """
        用于获取 子频道 channel_id 下用户 user_id 的权限

        :param channel_id: 子频道id
        :param user_id: 用户id
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(f'{self.bot_url}/channels/{channel_id}/members/{user_id}/permissions')
        return regular_temp(return_)

    def put_channel_member_permission(self, channel_id: str, user_id: str, add: Optional[str] = None,
                                      remove: Optional[str] = None) -> reply_model.put_channel_mr_permission():
        """
        用于修改子频道 channel_id 下用户 user_id 的权限

        :param channel_id: 子频道id
        :param user_id: 用户id
        :param add: 需要添加的权限，string格式，可选：1，2，4
        :param remove:需要删除的权限，string格式，可选：1，2，4
        :return: 返回的.result显示是否成功
        """
        if not all([items in ('1', '2', '4', None) for items in (add, remove)]):
            return sdk_error_temp('注意add或remove的值只能为1、2或4的文本格式内容')
        json_ = {'add': add, 'remove': remove}
        return_ = self.__session.put(f'{self.bot_url}/channels/{channel_id}/members/{user_id}/permissions',
                                     json=json_)
        return http_temp(return_, 204)

    def get_channel_role_permission(self, channel_id: str, role_id: str) -> \
            reply_model.get_channel_role_permission():
        """
        用于获取 子频道 channel_id 下身份组 role_id 的权限

        :param channel_id: 子频道id
        :param role_id: 身份组id
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(f'{self.bot_url}/channels/{channel_id}/roles/{role_id}/permissions')
        return regular_temp(return_)

    def put_channel_role_permission(self, channel_id: str, role_id: str, add: Optional[str] = None,
                                    remove: Optional[str] = None) -> reply_model.put_channel_mr_permission():
        """
        用于修改子频道 channel_id 下身份组 role_id 的权限

        :param channel_id: 子频道id
        :param role_id: 身份组id
        :param add: 需要添加的权限，string格式，可选：1，2，4
        :param remove:需要删除的权限，string格式，可选：1，2，4
        :return: 返回的.result显示是否成功
        """
        if not all([items in ('1', '2', '4', None) for items in (add, remove)]):
            return sdk_error_temp('注意add或remove的值只能为1、2或4的文本格式内容')
        json_ = {'add': add, 'remove': remove}
        return_ = self.__session.put(f'{self.bot_url}/channels/{channel_id}/roles/{role_id}/permissions',
                                     json=json_)
        return http_temp(return_, 204)

    def get_message_info(self, channel_id: str, message_id: str) -> reply_model.get_message_info():
        """
        用于获取子频道 channel_id 下的消息 message_id 的详情

        :param channel_id: 频道ID
        :param message_id: 目标消息ID
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(f'{self.bot_url}/channels/{channel_id}/messages/{message_id}')
        return regular_temp(return_)

    def send_msg(self, channel_id: str, content: Optional[str] = None, image: Optional[str] = None,
                 file_image: Optional[Union[bytes, BinaryIO, str, PathLike[str]]] = None,
                 message_id: Optional[str] = None, event_id: Optional[str] = None,
                 message_reference_id: Optional[str] = None,
                 ignore_message_reference_error: Optional[bool] = None) -> reply_model.send_msg():
        """
        发送普通消息的API

        :param channel_id: 子频道id
        :param content: 消息文本（选填，此项与image至少需要有一个字段，否则无法下发消息）
        :param image: 图片url，不可发送本地图片（选填，此项与msg至少需要有一个字段，否则无法下发消息）
        :param file_image: 本地图片，可选三种方式传参，具体可参阅github中的example_10或帮助文档
        :param message_id: 消息id（选填）
        :param event_id: 事件id（选填）
        :param message_reference_id: 引用消息的id（选填）
        :param ignore_message_reference_error: 是否忽略获取引用消息详情错误，默认否（选填）
        :return: 返回的.data中为解析后的json数据
        """
        if message_reference_id is not None:
            if ignore_message_reference_error is None:
                ignore_message_reference_error = False
            json_ = {'content': content, 'msg_id': message_id, 'event_id': event_id, 'image': image,
                     'message_reference': {'message_id': message_reference_id,
                                           'ignore_get_message_error': ignore_message_reference_error}}
        else:
            json_ = {'content': content, 'msg_id': message_id, 'event_id': event_id, 'image': image}
        if file_image is not None:
            if isinstance(file_image, BufferedReader):
                file_image = file_image.read()
            elif isinstance(file_image, str):
                if exists(file_image):
                    with open(file_image, 'rb') as img:
                        file_image = img.read()
                else:
                    return sdk_error_temp('目标图片路径不存在，无法发送')
            files = {'file_image': file_image}
            return_ = self.__session.post(self.bot_url + '/channels/{}/messages'.format(channel_id), data=json_,
                                          files=files)
        else:
            return_ = self.__session.post(self.bot_url + '/channels/{}/messages'.format(channel_id), json=json_)
        return regular_temp(return_)

    def send_embed(self, channel_id: str, title: Optional[str] = None, content: Optional[list[str]] = None,
                   image: Optional[str] = None, prompt: Optional[str] = None, message_id: Optional[str] = None,
                   event_id: Optional[str] = None) -> reply_model.send_msg():
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
        json_ = {"embed": {"title": title, "prompt": prompt, "thumbnail": {"url": image}, "fields": []},
                 'msg_id': message_id, 'event_id': event_id}
        if content is not None:
            for items in content:
                json_["embed"]["fields"].append({"name": items})
        return_ = self.__session.post(self.bot_url + '/channels/{}/messages'.format(channel_id), json=json_)
        return regular_temp(return_)

    def send_ark_23(self, channel_id: str, content: list[str], link: list[str], desc: Optional[str] = None,
                    prompt: Optional[str] = None, message_id: Optional[str] = None,
                    event_id: Optional[str] = None) -> reply_model.send_msg():
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
        if len(content) != len(link):
            return sdk_error_temp('注意内容列表长度应与链接列表长度一致')
        json_ = {"ark": {"template_id": 23,
                         "kv": [{"key": "#DESC#", "value": desc}, {"key": "#PROMPT#", "value": prompt},
                                {"key": "#LIST#", "obj": []}]}, 'msg_id': message_id, 'event_id': event_id}
        for i, items in enumerate(content):
            json_["ark"]["kv"][2]["obj"].append({"obj_kv": [{"key": "desc", "value": items},
                                                            {"key": "link", "value": link[i]}]})
        return_ = self.__session.post(self.bot_url + '/channels/{}/messages'.format(channel_id),
                                      json=json_)
        return regular_temp(return_)

    def send_ark_24(self, channel_id: str, title: Optional[str] = None, content: Optional[str] = None,
                    subtitile: Optional[str] = None, link: Optional[str] = None, image: Optional[str] = None,
                    desc: Optional[str] = None, prompt: Optional[str] = None, message_id: Optional[str] = None,
                    event_id: Optional[str] = None) -> reply_model.send_msg():
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
        json_ = {'ark': {'template_id': 24, 'kv': [{'key': '#DESC#', 'value': desc},
                                                   {'key': '#PROMPT#', 'value': prompt},
                                                   {'key': '#TITLE#', 'value': title},
                                                   {'key': '#METADESC#', 'value': content},
                                                   {'key': '#IMG#', 'value': image},
                                                   {'key': '#LINK#', 'value': link},
                                                   {'key': '#SUBTITLE#', 'value': subtitile}]},
                 'msg_id': message_id, 'event_id': event_id}
        return_ = self.__session.post(self.bot_url + '/channels/{}/messages'.format(channel_id),
                                      json=json_)
        return regular_temp(return_)

    def send_ark_37(self, channel_id: str, title: Optional[str] = None, content: Optional[str] = None,
                    link: Optional[str] = None, image: Optional[str] = None, prompt: Optional[str] = None,
                    message_id: Optional[str] = None, event_id: Optional[str] = None) -> reply_model.send_msg():
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
        json_ = {"ark": {"template_id": 37, "kv": [{"key": "#PROMPT#", "value": prompt},
                                                   {"key": "#METATITLE#", "value": title},
                                                   {"key": "#METASUBTITLE#", "value": content},
                                                   {"key": "#METACOVER#", "value": image},
                                                   {"key": "#METAURL#", "value": link}]},
                 'msg_id': message_id, 'event_id': event_id}
        return_ = self.__session.post(self.bot_url + '/channels/{}/messages'.format(channel_id),
                                      json=json_)
        return regular_temp(return_)

    def delete_msg(self, channel_id: str, message_id: str, hidetip: bool = False) -> reply_model.delete_msg():
        """
        撤回消息的API，注意一般情况下仅私域可以使用

        :param channel_id: 子频道id
        :param message_id: 需撤回消息的消息id
        :param hidetip: 是否隐藏提示小灰条，True为隐藏，False为显示（选填）
        :return: 返回的.result显示是否成功
        """
        self.check_warning('撤回消息')
        return_ = self.__session.delete(
            self.bot_url + f'/channels/{channel_id}/messages/{message_id}?hidetip={str(hidetip).lower()}')
        return http_temp(return_, 200)

    def get_guild_setting(self, guild_id: str) -> reply_model.get_guild_setting():
        """
        用于获取机器人在频道 guild_id 内的消息频率设置

        :param guild_id: 频道id
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(f'{self.bot_url}/guilds/{guild_id}/message/setting')
        return regular_temp(return_)

    def create_dm_guild(self, target_id: str, guild_id: str) -> reply_model.create_dm_guild():
        """
        当机器人主动跟用户私信时，创建并获取一个虚拟频道id的API

        :param target_id: 目标用户id
        :param guild_id: 机器人跟目标用户所在的频道id
        :return: 返回的.data中为解析后的json数据，注意发送私信仅需要使用guild_id这一项虚拟频道id的数据
        """
        json_ = {"recipient_id": target_id, "source_guild_id": guild_id}
        return_ = self.__session.post(self.bot_url + '/users/@me/dms', json=json_)
        return regular_temp(return_)

    def send_dm(self, guild_id: str, content: Optional[str] = None, image: Optional[str] = None,
                file_image: Optional[Union[bytes, BinaryIO, str, PathLike[str]]] = None,
                message_id: Optional[str] = None, event_id: Optional[str] = None,
                message_reference_id: Optional[str] = None,
                ignore_message_reference_error: Optional[bool] = None) -> reply_model.send_msg():
        """
        私信用户的API

        :param guild_id: 虚拟频道id（非子频道id），从用户主动私信机器人的事件、或机器人主动创建私信的API中获取
        :param content: 消息内容文本
        :param image: 图片url，不可发送本地图片（选填，此项与msg至少需要有一个字段，否则无法下发消息）
        :param file_image: 本地图片，可选三种方式传参，具体可参阅github中的example_10或帮助文档
        :param message_id: 消息id（选填）
        :param event_id: 事件id（选填）
        :param message_reference_id: 引用消息的id（选填）
        :param ignore_message_reference_error: 是否忽略获取引用消息详情错误，默认否（选填）
        :return: 返回的.data中为解析后的json数据
        """
        if message_reference_id is not None:
            if ignore_message_reference_error is None:
                ignore_message_reference_error = False
            json_ = {'content': content, 'msg_id': message_id, 'event_id': event_id, 'image': image,
                     'message_reference': {'message_id': message_reference_id,
                                           'ignore_get_message_error': ignore_message_reference_error}}
        else:
            json_ = {'content': content, 'msg_id': message_id, 'event_id': event_id, 'image': image}
        if file_image is not None:
            if isinstance(file_image, BufferedReader):
                file_image = file_image.read()
            elif isinstance(file_image, str):
                if exists(file_image):
                    with open(file_image, 'rb') as img:
                        file_image = img.read()
                else:
                    return sdk_error_temp('目标图片路径不存在，无法发送')
            files = {'file_image': file_image}
            return_ = self.__session.post(self.bot_url + f'/dms/{guild_id}/messages', data=json_, files=files)
        else:
            return_ = self.__session.post(self.bot_url + f'/dms/{guild_id}/messages', json=json_)
        return regular_temp(return_)

    def delete_dm_msg(self, guild_id: str, message_id: str, hidetip: bool = False) -> reply_model.delete_msg():
        """
        用于撤回私信频道 guild_id 中 message_id 指定的私信消息。只能用于撤回机器人自己发送的私信

        :param guild_id: 虚拟频道id（非子频道id），从用户主动私信机器人的事件、或机器人主动创建私信的API中获取
        :param message_id: 需撤回消息的消息id
        :param hidetip: 是否隐藏提示小灰条，True为隐藏，False为显示（选填）
        :return: 返回的.result显示是否成功
        """
        self.check_warning('撤回私信消息')
        return_ = self.__session.delete(self.bot_url +
                                        f'/dms/{guild_id}/messages/{message_id}?hidetip={str(hidetip).lower()}')
        return http_temp(return_, 200)

    def mute_all_member(self, guild_id: str, mute_end_timestamp: Optional[str], mute_seconds: Optional[str]) -> \
            reply_model.mute_member():
        """
        用于将频道的全体成员（非管理员）禁言

        :param guild_id: 频道id
        :param mute_end_timestamp: 禁言到期时间戳，绝对时间戳，单位：秒（与 mute_seconds 字段同时赋值的话，以该字段为准）
        :param mute_seconds: 禁言多少秒（两个字段二选一，默认以 mute_end_timestamp 为准）
        :return: 返回的.result显示是否成功
        """
        json_ = {'mute_end_timestamp': mute_end_timestamp, 'mute_seconds': mute_seconds}
        return_ = self.__session.patch(self.bot_url + f'/guilds/{guild_id}/mute', json=json_)
        return http_temp(return_, 204)

    def mute_member(self, guild_id: str, user_id: str, mute_end_timestamp: Optional[str],
                    mute_seconds: Optional[str]) -> reply_model.mute_member():
        """
        用于禁言频道 guild_id 下的成员 user_id

        :param guild_id: 频道id
        :param user_id: 目标成员的用户ID
        :param mute_end_timestamp: 禁言到期时间戳，绝对时间戳，单位：秒（与 mute_seconds 字段同时赋值的话，以该字段为准）
        :param mute_seconds: 禁言多少秒（两个字段二选一，默认以 mute_end_timestamp 为准）
        :return: 返回的.result显示是否成功
        """
        json_ = {'mute_end_timestamp': mute_end_timestamp, 'mute_seconds': mute_seconds}
        return_ = self.__session.patch(self.bot_url + f'/guilds/{guild_id}/members/{user_id}/mute',
                                       json=json_)
        return http_temp(return_, 204)

    def mute_members(self, guild_id: str, user_id: list[str], mute_end_timestamp: Optional[str],
                     mute_seconds: Optional[str]) -> reply_model.mute_members():
        """
        用于将频道的指定批量成员（非管理员）禁言

        :param guild_id: 频道id
        :param user_id: 目标成员的用户ID列表
        :param mute_end_timestamp: 禁言到期时间戳，绝对时间戳，单位：秒（与 mute_seconds 字段同时赋值的话，以该字段为准）
        :param mute_seconds: 禁言多少秒（两个字段二选一，默认以 mute_end_timestamp 为准）
        :return: 返回的.data中为解析后的json数据
        """
        json_ = {'mute_end_timestamp': mute_end_timestamp, 'mute_seconds': mute_seconds, 'user_ids': user_id}
        return_ = self.__session.patch(self.bot_url + f'/guilds/{guild_id}/mute', json=json_)
        trace_id = return_.headers['X-Tps-Trace-Id']
        try:
            return_dict = return_.json()
            if return_.status_code == 200:
                result = False
            else:
                result = True
            return objectize({'data': return_dict, 'trace_id': trace_id, 'result': result})
        except JSONDecodeError:
            return objectize({'data': None, 'trace_id': trace_id, 'result': False})

    def create_announce(self, guild_id, channel_id: Optional[str] = None, message_id: Optional[str] = None,
                        announces_type: Optional[int] = None, recommend_channels_id: Optional[list[str]] = None,
                        recommend_channels_introduce: Optional[list[str]] = None) -> reply_model.create_announce():
        """
        用于创建频道全局公告，公告类型分为 消息类型的频道公告 和 推荐子频道类型的频道公告

        :param guild_id: 频道id
        :param channel_id: 子频道id，message_id 有值则为必填
        :param message_id: 消息id，此项有值则优选将某条消息设置为成员公告
        :param announces_type: 公告类别 0：成员公告，1：欢迎公告，默认为成员公告
        :param recommend_channels_id: 推荐子频道id列表，会一次全部替换推荐子频道列表
        :param recommend_channels_introduce: 推荐子频道推荐语列表，列表长度应与recommend_channels_id一致
        :return: 返回的.data中为解析后的json数据
        """
        json_ = {"channel_id": channel_id, "message_id": message_id, "announces_type": announces_type,
                 "recommend_channels": []}
        if recommend_channels_id is not None and recommend_channels_id:
            if len(recommend_channels_id) == len(recommend_channels_introduce):
                for i, items in enumerate(recommend_channels_id):
                    json_["recommend_channels"].append({"channel_id": items,
                                                        "introduce": recommend_channels_introduce[i]})
            else:
                return sdk_error_temp('注意推荐子频道ID列表长度，应与推荐子频道推荐语列表长度一致')
        return_ = self.__session.post(self.bot_url + f'/guilds/{guild_id}/announces', json=json_)
        return regular_temp(return_)

    def delete_announce(self, guild_id: str, message_id: str = 'all') -> reply_model.delete_announce():
        """
        用于删除频道 guild_id 下指定 message_id 的全局公告

        :param guild_id: 频道id
        :param message_id: message_id有值时会校验message_id合法性；若不校验，请将message_id设置为all（默认为all）
        :return: 返回的.result显示是否成功
        """
        return_ = self.__session.delete(self.bot_url + f'/guilds/{guild_id}/announces/{message_id}')
        return http_temp(return_, 204)

    def create_pinmsg(self, channel_id: str, message_id: str) -> reply_model.pinmsg():
        """
        用于添加子频道 channel_id 内的精华消息

        :param channel_id: 子频道id
        :param message_id: 目标消息id
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.put(self.bot_url + f'/channels/{channel_id}/pins/{message_id}')
        return regular_temp(return_)

    def delete_pinmsg(self, channel_id: str, message_id: str) -> reply_model.delete_pinmsg():
        """
        用于删除子频道 channel_id 下指定 message_id 的精华消息

        :param channel_id: 子频道id
        :param message_id: 目标消息id
        :return: 返回的.result显示是否成功
        """
        return_ = self.__session.delete(self.bot_url + f'/channels/{channel_id}/pins/{message_id}')
        return http_temp(return_, 204)

    def get_pinmsg(self, channel_id: str) -> reply_model.pinmsg():
        """
        用于获取子频道 channel_id 内的精华消息

        :param channel_id: 子频道id
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(self.bot_url + f'/channels/{channel_id}/pins')
        return regular_temp(return_)

    def get_schedules(self, channel_id: str, since: Optional[int] = None) -> reply_model.get_schedules():
        """
        用于获取channel_id指定的子频道中当天的日程列表

        :param channel_id: 日程子频道id
        :param since: 起始时间戳(ms)
        :return: 返回的.data中为解析后的json数据
        """
        json_ = {"since": since}
        return_ = self.__session.get(self.bot_url + f'/channels/{channel_id}/schedules', json=json_)
        return regular_temp(return_)

    def get_schedule_info(self, channel_id: str, schedule_id: str) -> reply_model.schedule_info():
        """
        获取日程子频道 channel_id 下 schedule_id 指定的的日程的详情

        :param channel_id: 日程子频道id
        :param schedule_id: 日程id
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(self.bot_url + f'/channels/{channel_id}/schedules/{schedule_id}')
        return regular_temp(return_)

    def create_schedule(self, channel_id: str, schedule_name: str, start_timestamp: str, end_timestamp: str,
                        jump_channel_id: str, remind_type: str) -> reply_model.schedule_info():
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
        json_ = {"schedule": {"name": schedule_name, "start_timestamp": start_timestamp,
                              "end_timestamp": end_timestamp, "jump_channel_id": jump_channel_id,
                              "remind_type": remind_type}}
        return_ = self.__session.post(self.bot_url + f'/channels/{channel_id}/schedules',
                                      json=json_)
        return regular_temp(return_)

    def patch_schedule(self, channel_id: str, schedule_id: str, schedule_name: str, start_timestamp: str,
                       end_timestamp: str, jump_channel_id: str, remind_type: str) -> reply_model.schedule_info():
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
        json_ = {"schedule": {"name": schedule_name, "start_timestamp": start_timestamp,
                              "end_timestamp": end_timestamp, "jump_channel_id": jump_channel_id,
                              "remind_type": remind_type}}
        return_ = self.__session.patch(self.bot_url + f'/channels/{channel_id}/schedules/{schedule_id}',
                                       json=json_)
        return regular_temp(return_)

    def delete_schedule(self, channel_id: str, schedule_id: str) -> reply_model.delete_schedule():
        """
        用于删除日程子频道 channel_id 下 schedule_id 指定的日程

        :param channel_id: 日程子频道id
        :param schedule_id: 日程id
        :return: 返回的.result显示是否成功
        """
        return_ = self.__session.delete(self.bot_url + f'/channels/{channel_id}/schedules/{schedule_id}')
        return http_temp(return_, 204)

    def create_reaction(self, channel_id: str, message_id: str, type_: str, id_: str) -> reply_model.reactions():
        """
        对message_id指定的消息进行表情表态

        :param channel_id: 子频道id
        :param message_id: 目标消息id
        :param type_: 表情类型
        :param id_: 表情id
        :return: 返回的.result显示是否成功
        """
        return_ = self.__session.put(self.bot_url +
                                     f'/channels/{channel_id}/messages/{message_id}/reactions/{type_}/{id_}')
        return http_temp(return_, 204)

    def delete_reaction(self, channel_id: str, message_id: str, type_: str, id_: str) -> reply_model.reactions():
        """
        删除自己对message_id指定消息的表情表态

        :param channel_id: 子频道id
        :param message_id: 目标消息id
        :param type_: 表情类型
        :param id_: 表情id
        :return: 返回的.result显示是否成功
        """
        return_ = self.__session.delete(self.bot_url +
                                        f'/channels/{channel_id}/messages/{message_id}/reactions/{type_}/{id_}')
        return http_temp(return_, 204)

    def get_reaction_users(self, channel_id: str, message_id: str, type_: str, id_: str) -> \
            reply_model.get_reaction_users():
        """
        拉取对消息 message_id 指定表情表态的用户列表

        :param channel_id: 子频道id
        :param message_id: 目标消息id
        :param type_: 表情类型
        :param id_: 表情id
        :return: 返回的.data中为解析后的json数据列表
        """
        return_ = self.__session.get(self.bot_url + f'/channels/{channel_id}/messages/{message_id}/reactions/'
                                                    f'{type_}/{id_}?cookie=&limit=50')
        trace_ids = [return_.headers['X-Tps-Trace-Id']]
        all_users = []
        try:
            return_dict = return_.json()
            if isinstance(return_dict, dict) and 'code' in return_dict.keys():
                all_users.append(return_dict)
                results = [False]
            else:
                for items in return_dict['users']:
                    all_users.append(items)
                results = [True]
                while True:
                    if return_dict['is_end']:
                        break
                    return_ = self.__session.get(
                        self.bot_url + f'/channels/{channel_id}/messages/{message_id}/reactions/'
                                       f'{type_}/{id_}?cookies={return_dict["cookie"]}')
                    trace_ids.append(return_.headers['X-Tps-Trace-Id'])
                    return_dict = return_.json()
                    if isinstance(return_dict, dict) and 'code' in return_dict.keys():
                        results.append(False)
                        all_users.append(return_dict)
                        break
                    else:
                        results.append(True)
                        for items in return_dict['users']:
                            all_users.append(items)
            return objectize({'data': all_users, 'trace_id': trace_ids, 'result': results})
        except JSONDecodeError:
            return objectize({'data': None, 'trace_id': trace_ids, 'result': [False]})

    def control_audio(self, channel_id: str, status: int, audio_url: Optional[str] = None,
                      text: Optional[str] = None) -> reply_model.audio():
        """
        用于控制子频道 channel_id 下的音频

        :param channel_id: 子频道id
        :param status: 播放状态
        :param audio_url: 音频数据的url，可选，status为0时传
        :param text: 状态文本（比如：简单爱-周杰伦），可选，status为0时传，其他操作不传
        :return: 返回的.result显示是否成功
        """
        json_ = {"audio_url": audio_url, "text": text, "status": status}
        return_ = self.__session.post(self.bot_url + f'/channels/{channel_id}/audio',
                                      json=json_)
        return empty_temp(return_)

    def bot_on_mic(self, channel_id: str) -> reply_model.audio():
        """
        机器人在 channel_id 对应的语音子频道上麦

        :param channel_id: 子频道id
        :return: 返回的.result显示是否成功
        """
        return_ = self.__session.put(self.bot_url + f'/channels/{channel_id}/mic')
        return empty_temp(return_)

    def bot_off_mic(self, channel_id: str) -> reply_model.audio():
        """
        机器人在 channel_id 对应的语音子频道下麦

        :param channel_id: 子频道id
        :return: 返回的.result显示是否成功
        """
        return_ = self.__session.delete(self.bot_url + f'/channels/{channel_id}/mic')
        return empty_temp(return_)

    def get_threads(self, channel_id) -> reply_model.get_threads():
        """
        获取子频道下的帖子列表

        :param channel_id: 目标论坛子频道id
        :return: 返回的.data中为解析后的json数据列表
        """
        self.check_warning('获取帖子列表')
        return_ = self.__session.get(self.bot_url + f'/channels/{channel_id}/threads')
        trace_ids = [return_.headers['X-Tps-Trace-Id']]
        all_threads = []
        try:
            return_dict = return_.json()
            if isinstance(return_dict, dict) and 'code' in return_dict.keys():
                all_threads.append(return_dict)
                results = [False]
            else:
                for items in return_dict['threads']:
                    if 'thread_info' in items.keys() and 'content' in items['thread_info'].keys():
                        items['thread_info']['content'] = loads(items['thread_info']['content'])
                    all_threads.append(items)
                results = [True]
                while True:
                    if return_dict['is_finish']:
                        break
                    return_ = self.__session.get(self.bot_url + f'/channels/{channel_id}/threads')
                    trace_ids.append(return_.headers['X-Tps-Trace-Id'])
                    return_dict = return_.json()
                    if isinstance(return_dict, dict) and 'code' in return_dict.keys():
                        results.append(False)
                        all_threads.append(return_dict)
                        break
                    else:
                        results.append(True)
                        for items in return_dict['threads']:
                            if 'thread_info' in items.keys() and 'content' in items['thread_info'].keys():
                                items['thread_info']['content'] = loads(items['thread_info']['content'])
                            all_threads.append(items)
            return objectize({'data': all_threads, 'trace_id': trace_ids, 'result': results})
        except JSONDecodeError:
            return objectize({'data': None, 'trace_id': trace_ids, 'result': [False]})

    def get_thread_info(self, channel_id: str, thread_id: str) -> reply_model.get_thread_info():
        """
        获取子频道下的帖子详情

        :param channel_id: 目标论坛子频道id
        :param thread_id: 帖子id
        :return: 返回的.data中为解析后的json数据
        """
        self.check_warning('获取帖子详情')
        return_ = self.__session.get(self.bot_url + f'/channels/{channel_id}/threads/{thread_id}')
        return regular_temp(return_)

    def create_thread(self, channel_id: str, title: str, content: str, format_: int) -> reply_model.create_thread():
        """
        创建帖子，创建成功后，返回创建成功的任务ID

        :param channel_id: 目标论坛子频道id
        :param title: 帖子标题
        :param content: 帖子内容（具体格式根据format_判断）
        :param format_: 帖子文本格式（1：普通文本、2：HTML、3：Markdown、4：Json）
        :return: 返回的.data中为解析后的json数据
        """
        self.check_warning('发表帖子')
        json_ = {'title': title, 'content': content, 'format': format_}
        return_ = self.__session.put(self.bot_url + f'/channels/{channel_id}/threads', json=json_)
        return regular_temp(return_)

    def delete_thread(self, channel_id: str, thread_id: str) -> reply_model.delete_thread():
        """
        删除指定子频道下的某个帖子

        :param channel_id: 目标论坛子频道id
        :param thread_id: 帖子id
        :return: 返回的.result显示是否成功
        """
        self.check_warning('删除帖子')
        return_ = self.__session.delete(self.bot_url + f'/channels/{channel_id}/threads/{thread_id}')
        return http_temp(return_, 204)

    def get_guild_permissions(self, guild_id: str) -> reply_model.get_guild_permissions():
        """
        获取机器人在频道 guild_id 内可以使用的权限列表

        :param guild_id: 频道id
        :return: 返回的.data中为解析后的json数据
        """
        return_ = self.__session.get(self.bot_url + f'/guilds/{guild_id}/api_permission')
        trace_id = return_.headers['X-Tps-Trace-Id']
        try:
            return_dict = return_.json()
            if isinstance(return_dict, dict) and 'code' in return_dict.keys():
                result = False
            else:
                result = True
                for i in range(len(return_dict['apis'])):
                    api = api_converter_re(return_dict['apis'][i]['method'], return_dict['apis'][i]['path'])
                    return_dict['apis'][i]['api'] = api
            return objectize({'data': return_dict, 'trace_id': trace_id, 'result': result})
        except JSONDecodeError:
            return objectize({'data': None, 'trace_id': trace_id, 'result': False})

    def create_permission_demand(self, guild_id: str, channel_id: str, api: str, desc: str or None) -> \
            reply_model.create_permission_demand():
        """
        发送频道API接口权限授权链接到频道

        :param guild_id: 频道id
        :param channel_id: 子频道id
        :param api: 需求权限的API在sdk的名字
        :param desc: 机器人申请对应的API接口权限后可以使用功能的描述
        :return: 返回成功或不成功
        """
        path, method = api_converter(api)
        if not path:
            return sdk_error_temp('目标API不存在，请检查API名称是否正确')
        json_ = {"channel_id": channel_id, "api_identify": {"path": path, "method": method.upper()}, "desc": desc}
        return_ = self.__session.post(self.bot_url + f'/guilds/{guild_id}/api_permission/demand',
                                      json=json_)
        return empty_temp(return_)

    def start(self):
        """
        开始运行机器人的函数，在唤起此函数后的代码将不能运行，如需运行后续代码，请以多进程方式唤起此函数，以下是一个简单的唤起流程：

        >>> from qg_botsdk.qg_bot import BOT
        >>> bot = BOT(bot_id='xxx', bot_token='xxx')
        >>> bot.start()

        .. seealso::
            更多教程和相关资讯可参阅：
            https://thoughts.teambition.com/sharespace/6289c429eb27e90041a58b57/docs/6289c429eb27e90041a58b52
        """
        if not self.running:
            self.running = True
            gateway = self.__session.get(self.bot_url + '/gateway/bot').json()
            if 'url' not in gateway.keys():
                raise type('IdTokenError', (Exception,), {})(
                    '你输入的 bot_id 和/或 bot_token 错误，无法连接使用机器人\n如尚未有相关票据，'
                    '请参阅 https://thoughts.teambition.com/share/627533408adeb10041b935b1#title=快速入门 了解相关详情')
            url = gateway["url"]
            self.logger.debug('[机器人ws地址] ' + url)
            _shard = gateway["shards"]
            self.logger.debug('[建议分片数] ' + str(_shard))
            if _shard > self.max_shard:
                _shard = self.max_shard
                self.logger.info('[注意] 由于最大分片数少于建议分片数，分片数已自动调整为 ' + str(self.max_shard))
            if self.__repeat_function is not None:
                self.__main_loop.create_task(self.__time_event_check())
            for shard_no in range(0, _shard):
                self.__bot_classes.append(
                    BotWs(self.__session, self.logger, _shard, shard_no, url, self.bot_id, self.bot_token,
                          self.bot_url, self.__on_msg_function, self.__on_dm_function, self.__on_delete_function,
                          self.is_filter_self, self.__on_guild_event_function, self.__on_guild_member_function,
                          self.__on_reaction_function, self.__on_interaction_function, self.__on_audit_function,
                          self.__on_forum_function, self.__on_audio_function, self.intents, self.msg_treat,
                          self.dm_treat, self.__on_start_function))
            if len(self.__bot_classes) == 1:
                self.__bot_classes[0].ws_starter()
            else:
                for bot_class in self.__bot_classes:
                    thread = Thread(target=bot_class.ws_starter)
                    thread.setDaemon(True)
                    thread.start()
                    self.__bot_threads.append(thread)
                self.__bot_threads[-1].join()
        else:
            self.logger.error('当前机器人已在运行中！')

    def close(self):
        """
        结束运行机器人的函数

        .. seealso::
            更多教程和相关资讯可参阅：
            https://thoughts.teambition.com/sharespace/6289c429eb27e90041a58b57/docs/6289c429eb27e90041a58b52
        """
        if self.running:
            self.running = False
            self.logger.info('所有WS链接已开始结束进程，请等待另一端完成握手并等待 TCP 连接终止')
            for bot_class in self.__bot_classes:
                bot_class.running = False
            while True:
                if self.__bot_classes[-1].ws.closed:
                    self.logger.info('所有WS链接已结束')
                    break
        else:
            self.logger.error('当前机器人没有运行！')
