# !/usr/bin/env python3
# encoding: utf-8
from os import getpid
from asyncio import get_event_loop, sleep
from time import sleep as t_sleep
from ssl import SSLContext
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from threading import Thread
from typing import Any, Callable, Union
from .logger import Logger
from .model import Model
from ._api_model import ReplyModel
from .qg_bot_ws import BotWs
from .utils import objectize, exception_handler
from .api import API

reply_model = ReplyModel()
retry = Retry(total=4, connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
version = '2.2.9'
pid = getpid()
print(f'本次程序进程ID：{pid} | SDK版本：{version} | 即将开始运行机器人……')
t_sleep(0.5)


class BOT:

    def __init__(self, bot_id: str, bot_token: str, bot_secret: str = None, is_private: bool = False,
                 is_sandbox: bool = False, max_shard: int = 5, no_permission_warning: bool = True,
                 is_async: bool = False, is_retry: bool = True):
        """
        机器人主体，输入BotAppID和密钥，并绑定函数后即可快速使用

        :param bot_id: 机器人平台后台BotAppID（开发者ID）项，必填
        :param bot_token: 机器人平台后台机器人令牌项，必填
        :param bot_secret: 机器人平台后台机器人密钥项，如需要使用安全检测功能需填写此项
        :param is_private: 机器人是否为私域机器人，默认False
        :param is_sandbox: 是否开启沙箱环境，默认False
        :param max_shard: 最大分片数，请根据配置自行判断，默认5
        :param no_permission_warning: 是否开启当机器人获取疑似权限不足的事件时的警告提示，默认开启
        :param is_async: 使用同步api还是异步api，默认False（使用同步）
        :param is_retry: 使用api时，如遇可重试的错误码是否自动进行重试
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
        self.__on_channel_event_function = None
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
        self.bot_headers = {'Authorization': "Bot " + str(self.bot_id) + "." + str(self.bot_token)}
        self.__ssl = SSLContext()
        self.__session = Session()
        self.__session.headers = self.bot_headers
        self.__session.keep_alive = False
        self.__session.mount('http://', adapter)
        self.__session.mount('https://', adapter)
        self.__bot_classes = []
        self.__bot_threads = []
        self.__loop = get_event_loop()
        self.msg_treat = True
        self.dm_treat = False
        self.no_permission_warning = no_permission_warning
        self.is_async = is_async
        if not is_async:
            self.api = API(self.bot_url, bot_id, bot_secret, self.__session, self.logger, self.check_warning,
                           self.__get_bot_id, is_retry)
        else:
            from .async_api import AsyncAPI
            self.api: Union[API, AsyncAPI] = AsyncAPI(self.bot_url, bot_id, bot_secret, self.__ssl, self.bot_headers,
                                                      self.logger, self.__loop, self.check_warning, self.__get_bot_id,
                                                      is_retry)

    async def __time_event_check(self):
        while self.running:
            try:
                if self.is_async:
                    await self.__repeat_function()
                else:
                    self.__repeat_function()
            except Exception as error:
                self.logger.error(error)
                self.logger.debug(exception_handler(error))
            await sleep(self.check_interval)

    def bind_msg(self, on_msg_function: Callable[[Model.MESSAGE], Any], treated_data: bool = True,
                 all_msg: bool = None):
        """
        用作绑定接收消息的函数，将根据机器人是否公域自动判断接收艾特或所有消息

        :param on_msg_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        :param treated_data: 是否返回经转义处理的文本，如是则会在返回的Object中添加一个treated_msg的子类，默认True
        :param all_msg: 是否无视公私域限制，强制开启全部消息接收，默认None（不判断此项参数）
        """
        self.__on_msg_function = on_msg_function
        if not treated_data:
            self.msg_treat = False
        if all_msg is None:
            if not self.is_private:
                self.intents = self.intents | 1 << 30
                self.logger.info('消息（所有消息）接收函数订阅成功')
            else:
                self.intents = self.intents | 1 << 9
                self.logger.info('消息（艾特消息）接收函数订阅成功')
        else:
            self.intents = self.intents | 1 << 30
            self.logger.info('消息（所有消息）接收函数订阅成功')

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

    def bind_channel_event(self, on_channel_event_function: Callable[[Model.CHANNELS], Any]):
        """
        用作绑定接收子频道信息的函数

        :param on_channel_event_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.__on_channel_event_function = on_channel_event_function
        self.intents = self.intents | 1 << 0
        self.logger.info('子频道事件订阅成功')

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

    def check_warning(self, name: str):
        if not self.is_private and self.no_permission_warning:
            self.logger.warning(f'请注意，一般公域机器人并不能使用{name}API，请检查自身是否拥有相关权限')

    def __get_bot_id(self):
        """
        获取机器人在频道场景的用户ID

        :return: 返回的.data中为机器人用户ID，如未注册则返回None
        """
        try:
            return objectize({'data': self.__bot_classes[0].bot_qid, 'result': True})
        except IndexError:
            return objectize({'data': None, 'result': False})

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
        try:
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
                    self.logger.warning('[注意] 由于最大分片数少于建议分片数，分片数已自动调整为 ' + str(self.max_shard))
                if self.__repeat_function is not None:
                    self.__loop.create_task(self.__time_event_check())
                for shard_no in range(0, _shard):
                    self.__bot_classes.append(
                        BotWs(self.__session, self.__ssl, self.logger, _shard, shard_no, url, self.bot_id,
                              self.bot_token, self.bot_url, self.__on_msg_function, self.__on_dm_function,
                              self.__on_delete_function, self.is_filter_self, self.__on_guild_event_function,
                              self.__on_channel_event_function, self.__on_guild_member_function,
                              self.__on_reaction_function, self.__on_interaction_function, self.__on_audit_function,
                              self.__on_forum_function, self.__on_audio_function, self.intents, self.msg_treat,
                              self.dm_treat, self.__on_start_function, self.is_async))
                if len(self.__bot_classes) == 1:
                    self.__bot_classes[0].ws_starter()
                else:
                    if self.is_async:
                        for bot_class in self.__bot_classes:
                            if bot_class != self.__bot_classes[-1]:
                                self.__loop.create_task(bot_class.ws_starter())
                            else:
                                bot_class.ws_starter()
                    else:
                        for bot_class in self.__bot_classes:
                            thread = Thread(target=bot_class.ws_starter)
                            thread.setDaemon(True)
                            thread.start()
                            self.__bot_threads.append(thread)
                        self.__bot_threads[-1].join()
            else:
                self.logger.error('当前机器人已在运行中！')
        except KeyboardInterrupt:
            exit()

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
            timeout = self.__loop.time() + 60
            while self.__loop.time() > timeout:
                t_sleep(1)
                if not self.__bot_classes[-1] or self.__bot_classes[-1].ws.closed:
                    self.logger.info('所有WS链接已结束')
                    return
            self.__bot_classes = []
            self.logger.info('判断超时，所有WS链接已强制结束')
        else:
            self.logger.error('当前机器人没有运行！')
