# encoding: utf-8
import asyncio
from json import loads, dumps
from json.decoder import JSONDecodeError
from websockets import connect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK, ConnectionClosed
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from ssl import SSLError, SSLContext
from time import sleep, time
from threading import Thread
from typing import Any, Callable
from sys import exc_info
from traceback import extract_tb
from .utils import objectize
from .logger import Logger
from .model import *


class BotWs:
    def __init__(self, logger, shard: int, shard_no: int, url: str, header: dict, bot_id: str, bot_token: str,
                 bot_url: str, on_msg_function: Callable[[Any], Any], on_dm_function: Callable[[Any], Any],
                 on_delete_function: Callable[[Any], Any], is_filter_self: bool,
                 on_guild_event_function: Callable[[Any], Any], on_guild_member_function: Callable[[Any], Any],
                 on_reaction_function: Callable[[Any], Any], on_interaction_function: Callable[[Any], Any],
                 on_audit_function: Callable[[Any], Any], on_forum_function: Callable[[Any], Any],
                 on_audio_function: Callable[[Any], Any], intents: int, msg_treat: bool, dm_treat: bool):
        self.logger = logger
        self.shard = shard
        self.shard_no = shard_no
        self.url = url
        self.header = header
        self.bot_id = bot_id
        self.bot_token = bot_token
        self.bot_url = bot_url
        self.on_msg_function = on_msg_function
        self.on_dm_function = on_dm_function
        self.on_delete_function = on_delete_function
        self.is_filter_self = is_filter_self
        self.on_guild_event_function = on_guild_event_function
        self.on_guild_member_function = on_guild_member_function
        self.on_reaction_function = on_reaction_function
        self.on_interaction_function = on_interaction_function
        self.on_audit_function = on_audit_function
        self.on_forum_function = on_forum_function
        self.on_audio_function = on_audio_function
        self.intents = intents
        self.msg_treat = msg_treat
        self.dm_treat = dm_treat
        self.bot_qid = ''
        self.heartbeat_time = 0
        self.loop = asyncio.new_event_loop()
        self.heart_paras = {"op": 1, "d": 'null'}
        self.reconnect_times = 0
        self.connection = True
        self.re_connect = False
        self.running = False
        self.session_id = 0
        self.heartbeat = None
        self.ws = None

    def hello(self):
        hello_json = {
            "op": 2,
            "d": {
                "token": "Bot " + str(self.bot_id) + "." + str(self.bot_token),
                "intents": self.intents,
                "shard": [self.shard_no, self.shard],
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": "pc"
                }
            }
        }
        return dumps(hello_json)

    async def ws_send(self, msg):
        try:
            await self.ws.send(msg)
        except (ConnectionClosedError, ConnectionClosedOK, SSLError):
            pass

    async def heart(self):
        while True:
            await asyncio.sleep(self.heartbeat_time)
            self.loop.create_task(self.ws_send(dumps(self.heart_paras)))

    def data_process(self, data):
        if data["t"] in ("AT_MESSAGE_CREATE", 'MESSAGE_CREATE'):
            if 'content' not in data["d"]:
                raw_msg = ''
            elif '<@!{}>'.format(self.bot_qid) in data["d"]["content"]:
                raw_msg = data["d"]["content"][data["d"]["content"].find('<@!{}>'.format(
                    self.bot_qid)) + len(self.bot_qid) + 4:].strip()
            else:
                raw_msg = data["d"]["content"]
            self.logger.info('收到来自“' + data["d"]["author"]["username"] + '--' + str(data["d"]["author"]["id"])
                             + '”的消息（' + raw_msg + '）')
            if self.on_msg_function is not None:
                if self.msg_treat:
                    if '\xa0' in raw_msg:
                        raw_msg = raw_msg.replace('\xa0', ' ')
                    if raw_msg[0] == '/':
                        raw_msg = raw_msg[1:]
                    raw_msg = raw_msg.replace('&amp;', '&')
                    raw_msg = raw_msg.replace('&lt;', '<')
                    raw_msg = raw_msg.replace('&gt;', '>')
                    data["d"]["treated_msg"] = raw_msg
                    data["d"]["t"] = data["t"]
                try:
                    Thread(target=self.on_msg_function, args=[objectize(data["d"])],
                           name=f'MsgThread-{str(data["s"])}').start()
                except Exception as error:
                    self.logger.error(error)
                    error_info = extract_tb(exc_info()[-1])[-1]
                    self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0],
                                                                                      error_info[1], error_info[2]))
                    pass
        elif data["t"] in ("MESSAGE_DELETE", "PUBLIC_MESSAGE_DELETE", "DIRECT_MESSAGE_DELETE"):
            if self.on_delete_function is not None:
                if self.is_filter_self:
                    target = data['d']['message']['author']['id']
                    op_user = data['d']['op_user']['id']
                    if op_user == target:
                        return
                data["d"]["t"] = data["t"]
                try:
                    Thread(target=self.on_delete_function, args=[objectize(data["d"])],
                           name=f'MsgThread-{str(data["s"])}').start()
                except Exception as error:
                    self.logger.error(error)
                    error_info = extract_tb(exc_info()[-1])[-1]
                    self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0],
                                                                                      error_info[1], error_info[2]))
                    pass
        elif data["t"] == "DIRECT_MESSAGE_CREATE":
            if 'content' not in data["d"]:
                raw_msg = ''
            else:
                raw_msg = data["d"]["content"]
            self.logger.info('收到来自“' + data["d"]["author"]["username"] + '--' + str(data["d"]["author"]["id"])
                             + '”的私信消息（' + raw_msg + '）')
            if self.on_dm_function is not None:
                if self.msg_treat:
                    if '\xa0' in raw_msg:
                        raw_msg = raw_msg.replace('\xa0', ' ')
                    if raw_msg[0] == '/':
                        raw_msg = raw_msg[1:]
                    raw_msg = raw_msg.strip()
                    raw_msg = raw_msg.replace('&amp;', '&')
                    raw_msg = raw_msg.replace('&lt;', '<')
                    raw_msg = raw_msg.replace('&gt;', '>')
                    data["d"]["treated_msg"] = raw_msg
                    data["d"]["t"] = data["t"]
                try:
                    Thread(target=self.on_dm_function, args=[objectize(data["d"])],
                           name=f'MsgThread-{str(data["s"])}').start()
                except Exception as error:
                    self.logger.error(error)
                    error_info = extract_tb(exc_info()[-1])[-1]
                    self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0],
                                                                                      error_info[1], error_info[2]))
                    pass
        elif data["t"] in ("GUILD_CREATE", "GUILD_UPDATE", "GUILD_DELETE", "CHANNEL_CREATE", "CHANNEL_UPDATE",
                           "CHANNEL_DELETE"):
            if self.on_guild_event_function is not None:
                try:
                    data["d"]["t"] = data["t"]
                    Thread(target=self.on_guild_event_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
                except Exception as error:
                    self.logger.error(error)
                    error_info = extract_tb(exc_info()[-1])[-1]
                    self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0],
                                                                                      error_info[1], error_info[2]))
                    pass
        elif data["t"] in ("GUILD_MEMBER_ADD", "GUILD_MEMBER_UPDATE", "GUILD_MEMBER_REMOVE"):
            if self.on_guild_member_function is not None:
                try:
                    data["d"]["t"] = data["t"]
                    Thread(target=self.on_guild_event_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
                except Exception as error:
                    self.logger.error(error)
                    error_info = extract_tb(exc_info()[-1])[-1]
                    self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0],
                                                                                      error_info[1], error_info[2]))
                    pass
        elif data["t"] in ("MESSAGE_REACTION_ADD", "MESSAGE_REACTION_REMOVE"):
            if self.on_reaction_function is not None:
                try:
                    data["d"]["t"] = data["t"]
                    Thread(target=self.on_guild_event_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
                except Exception as error:
                    self.logger.error(error)
                    error_info = extract_tb(exc_info()[-1])[-1]
                    self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0],
                                                                                      error_info[1], error_info[2]))
                    pass
        elif data["t"] == "INTERACTION_CREATE":
            if self.on_interaction_function is not None:
                try:
                    data["d"]["t"] = data["t"]
                    Thread(target=self.on_guild_event_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
                except Exception as error:
                    self.logger.error(error)
                    error_info = extract_tb(exc_info()[-1])[-1]
                    self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0],
                                                                                      error_info[1], error_info[2]))
                    pass
        elif data["t"] in ("MESSAGE_AUDIT_PASS", "MESSAGE_AUDIT_REJECT"):
            if self.on_audit_function is not None:
                try:
                    data["d"]["t"] = data["t"]
                    Thread(target=self.on_audit_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
                except Exception as error:
                    self.logger.error(error)
                    error_info = extract_tb(exc_info()[-1])[-1]
                    self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0],
                                                                                      error_info[1], error_info[2]))
                    pass
        elif data["t"] in ("FORUM_THREAD_CREATE", "FORUM_THREAD_UPDATE", "FORUM_THREAD_DELETE", "FORUM_POST_CREATE",
                           "FORUM_POST_DELETE", "FORUM_REPLY_CREATE", "FORUM_REPLY_DELETE",
                           "FORUM_PUBLISH_AUDIT_RESULT"):
            if self.on_forum_function is not None:
                try:
                    data["d"]["t"] = data["t"]
                    try:
                        data["d"]["thread_info"]["content"] = loads(data["d"]["thread_info"]["content"])
                    except JSONDecodeError:
                        pass
                    try:
                        data["d"]["thread_info"]["title"] = loads(data["d"]["thread_info"]["title"])
                    except JSONDecodeError:
                        pass
                    Thread(target=self.on_forum_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
                except Exception as error:
                    self.logger.error(error)
                    error_info = extract_tb(exc_info()[-1])[-1]
                    self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0],
                                                                                      error_info[1], error_info[2]))
                    pass
        elif data["t"] in ("AUDIO_START", "AUDIO_FINISH", "AUDIO_ON_MIC", "AUDIO_OFF_MIC"):
            if self.on_audio_function is not None:
                try:
                    data["d"]["t"] = data["t"]
                    Thread(target=self.on_audio_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
                except Exception as error:
                    self.logger.error(error)
                    error_info = extract_tb(exc_info()[-1])[-1]
                    self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0],
                                                                                      error_info[1], error_info[2]))
                    pass

    def main(self, msg):
        data = loads(msg)
        if data["op"] == 11:
            self.logger.info('心跳发送成功')
        else:
            if "t" in data and data["t"] != "READY":
                self.logger.info('[消息] ' + data["t"])
            self.logger.debug(data)
        if "s" in data and data["t"] != "READY" and data["t"] != "RESUMED":
            self.heart_paras["d"] = data["s"]
        if data["op"] == 10:
            self.heartbeat_time = float(int(data["d"]["heartbeat_interval"]) * 0.001)
            if not self.re_connect:
                self.loop.create_task(self.ws_send(self.hello()))
            else:
                reconnect_paras = {
                    "op": 6,
                    "d": {
                        "token": "Bot " + str(self.bot_id) + "." + str(self.bot_token),
                        "session_id": self.session_id,
                        "seq": 1337
                    }
                }
                self.loop.create_task(self.ws_send(dumps(reconnect_paras)))
        elif data["op"] == 0:
            if data["t"] == "READY":
                me_qid = session.get(self.bot_url + '/users/@me', headers=self.header).json()
                self.bot_qid = str(me_qid['id'])
                self.logger.info('机器人频道用户ID：' + self.bot_qid)
                self.connection = True
                self.session_id = data["d"]["session_id"]
                self.reconnect_times = 0
                tasks = [task.get_name() for task in asyncio.all_tasks()]
                if 'heartbeat_task' not in tasks:
                    self.heartbeat = self.loop.create_task(self.heart())
                    self.heartbeat.set_name('heartbeat_task')
                self.logger.info('连接成功，机器人开始运行')
            elif data["t"] == "RESUMED":
                self.connection = True
                self.reconnect_times = 0
                tasks = [task.get_name() for task in asyncio.all_tasks()]
                if 'heartbeat_task' not in tasks:
                    self.heartbeat = self.loop.create_task(self.heart())
                    self.heartbeat.set_name('heartbeat_task')
                self.logger.info('重连成功，机器人继续运行')
            else:
                self.data_process(data)

    async def connect(self):
        self.connection = True
        self.reconnect_times += 1
        try:
            async with connect(self.url, ssl=SSLContext()) as self.ws:
                try:
                    while self.ws.open:
                        message = await self.ws.recv()
                        if not self.running:
                            return
                        # yield message
                        self.main(message)
                except (ConnectionClosedError, SSLError):
                    self.connection = False
                    self.re_connect = True
                    if self.heartbeat is not None and not self.heartbeat.cancelled():
                        self.heartbeat.cancel()
                    self.logger.warning('BOT_WS链接已断开，正在尝试重连……')
                    return
                except (ConnectionClosed, ConnectionClosedOK):
                    if self.heartbeat is not None and not self.heartbeat.cancelled():
                        self.heartbeat.cancel()
                    return
                except Exception as error:
                    self.connection = False
                    self.re_connect = True
                    if self.heartbeat is not None and not self.heartbeat.cancelled():
                        self.heartbeat.cancel()
                    self.logger.error(error)
                    error_info = extract_tb(exc_info()[-1])[-1]
                    self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0], error_info[1], error_info[2]))
                    return
        except Exception as error:
            if self.heartbeat is not None and not self.heartbeat.cancelled():
                self.heartbeat.cancel()
            self.logger.error(error)
            error_info = extract_tb(exc_info()[-1])[-1]
            self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0], error_info[1], error_info[2]))
            return

    def ws_starter(self):
        self.running = True
        self.re_connect = False
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())
        while self.running:
            if self.reconnect_times <= 20:
                try:
                    self.loop.run_until_complete(self.connect())
                    sleep(5)
                except (ConnectionClosedError, ConnectionClosedOK, SSLError):
                    self.logger.warning('网络连线不稳定或已断开，请检查网络链接')
                    sleep(5)
                    pass
            else:
                try:
                    self.re_connect = False
                    self.loop.run_until_complete(self.connect())
                    sleep(5)
                except (ConnectionClosedError, ConnectionClosedOK, SSLError):
                    self.logger.warning('网络连线不稳定或已断开，请检查网络链接')
                    sleep(5)
                    pass

    def ws_closer(self):
        self.running = False
        try:
            if self.ws.open:
                self.ws.close()
            if self.heartbeat is not None and not self.heartbeat.cancelled():
                self.heartbeat.cancel()
        except NameError:
            pass


class BOT:

    def __init__(self, bot_id: str, bot_token: str, bot_secret: str = None, is_private: bool = True,
                 is_sandbox: bool = False, max_shard: int = 50):
        """
        机器人主体，输入BotAppID和密钥，并绑定函数后即可快速使用
        :param bot_id: 机器人平台后台BotAppID（开发者ID）项，必填
        :param bot_token: 机器人平台后台机器人令牌项，必填
        :param bot_secret: 机器人平台后台机器人密钥项，如需要使用安全检测功能需填写此项
        :param is_private: 机器人是否为私域机器人，默认True
        :param is_sandbox: 是否开启沙箱环境，默认False
        :param max_shard: 最大分片数，请根据配置自行判断，默认50
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
        self.shard_no = 0
        self.intents = 0
        self.on_delete_function = None
        self.on_msg_function = None
        self.on_dm_function = None
        self.on_guild_event_function = None
        self.on_guild_member_function = None
        self.on_reaction_function = None
        self.on_interaction_function = None
        self.on_audit_function = None
        self.on_forum_function = None
        self.on_audio_function = None
        self.repeat_function = None
        self.on_start_function = None
        self.is_filter_self = True
        self.check_interval = 10
        self.running = False
        self.header = {'Authorization': "Bot " + str(self.bot_id) + "." + str(self.bot_token)}
        self.bot_classes = []
        self.bot_threads = []
        # self.main_loop = asyncio.new_event_loop()
        gateway = session.get(self.bot_url + '/gateway/bot', headers=self.header).json()
        self.url = gateway["url"]
        self.logger.info('[机器人ws地址] ' + self.url)
        self.shard = gateway["shards"]
        self.logger.info('[建议分片数] ' + str(self.shard))
        if self.shard > max_shard:
            self.shard = max_shard
            self.logger.info('[注意] 由于最大分片数少于建议分片数，分片数已自动调整为 ' + str(max_shard))
        self.msg_treat = False
        self.dm_treat = False
        self.security_code = ''
        self.code_expire = 0

    def bind_msg(self, on_msg_function: Callable[[MESSAGE], Any], treated_data: bool = True):
        """
        用作注册接收消息的函数，将根据机器人是否公域自动判断接收艾特或所有消息
        :param on_msg_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        :param treated_data: 是否返回经转义处理的文本，如是则会在返回的Object中添加一个treated_msg的子类，默认True
        """
        self.on_msg_function = on_msg_function
        if self.is_private:
            self.intents = self.intents | 1 << 30
        else:
            self.intents = self.intents | 1 << 9
        if treated_data:
            self.msg_treat = True
        self.logger.info('消息接收函数订阅成功')

    def bind_dm(self, on_dm_function: Callable[[MESSAGE], Any], treated_data: bool = True):
        """
        用作注册接收私信消息的函数
        :param on_dm_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        :param treated_data: 是否返回经转义处理的文本，如是则会在返回的Object中添加一个treated_msg的子类，默认True
        """
        self.on_dm_function = on_dm_function
        self.intents = self.intents | 1 << 12
        if treated_data:
            self.dm_treat = True
        self.logger.info('私信接收函数订阅成功')

    def bind_msg_delete(self, on_delete_function: Callable[[MESSAGE_DELETE], Any], is_filter_self: bool = True):
        """
        用作注册接收消息撤回事件的函数，注册时将自动根据公域私欲注册艾特或全部消息，但不会主动注册私信事件
        :param on_delete_function:类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        :param is_filter_self: 是否过滤用户自行撤回的消息，只接受管理撤回事件
        """
        self.on_delete_function = on_delete_function
        self.is_filter_self = is_filter_self
        if self.is_private:
            self.intents = self.intents | 1 << 30
        else:
            self.intents = self.intents | 1 << 9
        self.logger.info('撤回事件订阅成功')

    def bind_guild_event(self, on_guild_event_function: Callable[[GUILDS], Any]):
        """
        用作注册接收频道信息的函数
        :param on_guild_event_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.on_guild_event_function = on_guild_event_function
        self.intents = self.intents | 1 << 0
        self.logger.info('频道事件订阅成功')

    def bind_guild_member(self, on_guild_member_function: Callable[[GUILD_MEMBERS], Any]):
        """
        用作注册接收频道信息的函数
        :param on_guild_member_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.on_guild_member_function = on_guild_member_function
        self.intents = self.intents | 1 << 1
        self.logger.info('频道成员事件订阅成功')

    def bind_reaction(self, on_reaction_function: Callable[[REACTION], Any]):
        """
        用作注册接收表情表态信息的函数
        :param on_reaction_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.on_reaction_function = on_reaction_function
        self.intents = self.intents | 1 << 10
        self.logger.info('表情表态事件订阅成功')

    def bind_interaction(self, on_interaction_function: Callable[[Any], Any]):
        """
        用作注册接收互动事件的函数，当前未有录入数据结构
        :param on_interaction_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.on_interaction_function = on_interaction_function
        self.intents = self.intents | 1 << 26
        self.logger.info('互动事件订阅成功')

    def bind_audit(self, on_audit_function: Callable[[MESSAGE_AUDIT], Any]):
        """
        用作注册接收互动事件的函数
        :param on_audit_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.on_audit_function = on_audit_function
        self.intents = self.intents | 1 << 27
        self.logger.info('审核事件订阅成功')

    def bind_forum(self, on_forum_function: Callable[[FORUMS_EVENT], Any]):
        """
        用作注册接收论坛事件的函数，仅私域机器人能注册此事件；
        当前仅可以接收FORUM_THREAD_CREATE、FORUM_THREAD_UPDATE、FORUM_THREAD_DELETE三个事件
        :param on_forum_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        if self.is_private:
            self.on_forum_function = on_forum_function
            self.intents = self.intents | 1 << 28
            self.logger.info('论坛事件订阅成功')
        else:
            self.logger.error('请注意，公域机器人不能注册论坛事件')

    def bind_audio(self, on_audio_function: Callable[[AUDIO_ACTION], Any]):
        """
        用作注册接收论坛事件的函数
        :param on_audio_function: 类型为function，该函数应包含一个参数以接收Object消息数据进行处理
        """
        self.on_audio_function = on_audio_function
        self.intents = self.intents | 1 << 29
        self.logger.info('音频事件订阅成功')

    def register_repeat_event(self, time_function: Callable[[], Any], check_interval: float or int = 10):
        """
        用作注册重复事件的函数，注册并开始机器人后，会根据间隔时间不断调用注册的函数
        :param time_function: 类型为function，该函数不应包含任何参数
        :param check_interval: 每多少秒检查调用一次时间事件函数，默认5
        """
        self.repeat_function = time_function
        self.check_interval = check_interval
        self.logger.info('重复事件注册成功')

    def register_start_event(self, on_start_function: Callable[[], Any]):
        """
        用作注册机器人开始时运行的函数，此函数不应有无限重复的内容
        :param on_start_function: 类型为function，该函数不应包含任何参数
        """
        self.on_start_function = on_start_function
        self.logger.info('开始事件注册成功')

    def time_event_check(self):
        while self.running:
            self.logger.new_logh()
            if self.repeat_function is not None:
                self.repeat_function()
            sleep(self.check_interval)

    def security_check_code(self):
        if self.bot_secret is None:
            self.logger.error('无法调用内容安全检测接口（备注：没有填入机器人密钥）')
            return None
        code = session.get(f'https://api.q.qq.com/api/getToken?grant_type=client_credential&appid={self.bot_id}&'
                           f'secret={self.bot_secret}').json()
        try:
            self.security_code = code['access_token']
            self.code_expire = time() + 7000
            return self.security_code
        except KeyError:
            self.logger.error('无法调用内容安全检测接口（备注：请检查机器人密钥是否正确）')
            return None

    def security_check(self, content):
        """
        腾讯小程序侧内容安全检测接口，使用此接口必须填入bot_secret密钥
        :param content: 需要检测的内容
        :return: True或False（bool），代表是否通过安全检测
        """
        if time() >= self.code_expire:
            if self.security_check_code() is None:
                return False
        check = session.post(f'https://api.q.qq.com/api/json/security/MsgSecCheck?access_token={self.security_code}',
                             headers=security_header, json={'content': content}).json()
        self.logger.debug(check)
        if check['errCode'] in (-1800110107, -1800110108):
            new_code = self.security_check_code()
            if new_code is None:
                return False
            check = session.post(f'https://api.q.qq.com/api/json/security/MsgSecCheck?access_token={new_code}',
                                 headers=security_header, json={'content': content}).json()
            self.logger.debug(check)
            if check['errCode'] == 0:
                return True
            return False
        elif check['errCode'] == 0:
            return True
        return False

    def send_msg(self, msg: str or None, msg_id: str or None = None, channel: str or None = None,
                 image: str or None = None) -> dict:
        """
        发送普通消息的API
        :param msg: 消息文本
        :param msg_id: 消息id，从机器人接收到的消息中获取，如无则消息为主动消息
        :param channel: 子频道id
        :param image: 图片url，不可发送本地图片
        :return: 返回解析后的json数据
        """
        post_json = {'content': msg, 'msg_id': msg_id, 'image': image}
        post_return = session.post(self.bot_url + '/channels/{}/messages'.format(channel),
                                   json=post_json, headers=self.header)
        post_return_dict = post_return.json()
        post_return_dict['header'] = post_return.headers
        if msg is None:
            self.logger.info('发送消息' + '[图片：' + image + '] 至子频道' + str(channel))
        elif image is not None:
            try:
                self.logger.info('发送（' + msg + '）' + '[图片：' + image + '] 至子频道' + str(channel))
            except UnicodeEncodeError:
                self.logger.info('发送消息 ' + '[图片：' + image + '] 至子频道' + str(channel))
                pass
        else:
            try:
                self.logger.info('发送（' + msg + '）至子频道' + str(channel))
            except UnicodeEncodeError:
                self.logger.info('发送消息至子频道' + str(channel))
                pass
        return post_return_dict

    def send_embed(self, title: str or None, content: list or None = None, msg_id: str or None = None,
                   channel: str or None = None, prompt: str or None = "机器人@了你", image: str or None = None) -> dict:
        """
        发送embed模板消息的API
        :param title: 标题文本
        :param content: 内容文本列表，每一项之间将存在分行
        :param msg_id: 消息id，从机器人接收到的消息中获取，如无则消息为主动消息
        :param channel: 子频道id
        :param prompt: 消息弹窗通知的文本内容
        :param image: 略缩图url，不可发送本地图片
        :return: 返回解析后的json数据
        """
        post_json = {
            "embed": {"title": title, "prompt": prompt, "thumbnail": {"url": image}, "fields": []}, 'msg_id': msg_id}
        for items in content:
            post_json["embed"]["fields"].append({"name": items})
        post_return = session.post(self.bot_url + '/channels/{}/messages'.format(channel),
                                   json=post_json, headers=self.header)
        post_return_dict = post_return.json()
        post_return_dict['header'] = post_return.headers
        self.logger.info('发送embed消息（' + str(content) + '）至子频道' + str(channel))
        return post_return_dict

    def send_ark_23(self, content: list, link: list or None, msg_id: str or None = None, channel: str or None = None,
                    prompt: str or None = None) -> dict:
        """
        发送ark（id=23）模板消息的API，注意一般仅私域机器人可使用此API
        :param content: 内容文本列表，每一项之间将存在分行
        :param link: 链接url列表，长度应与内容列一致。将根据对应位置顺序填充文本超链接，如文本不希望填充链接可使用空文本或None填充列表位置
        :param msg_id: 消息id，从机器人接收到的消息中获取，如无则消息为主动消息
        :param channel: 子频道id
        :param prompt: 消息弹窗通知的文本内容
        :return: 返回解析后的json数据
        """
        if len(content) != len(link):
            return {'code': '-1', 'return_msg': '注意内容列表长度应与链接列表长度一致'}
        post_json = {"ark": {"template_id": 23,
                             "kv": [{"key": "#DESC#", "value": prompt}, {"key": "#PROMPT#", "value": prompt},
                                    {"key": "#LIST#", "obj": []}]}, 'msg_id': msg_id}
        for i, items in enumerate(content):
            post_json["ark"]["kv"][2]["obj"].append({"obj_kv": [{"key": "desc", "value": items},
                                                                {"key": "link", "value": link[i]}]})
        post_return = session.post(self.bot_url + '/channels/{}/messages'.format(channel),
                                   json=post_json, headers=self.header)
        post_return_dict = post_return.json()
        post_return_dict['header'] = post_return.headers
        self.logger.info('发送ark[id=23]消息（' + '\n'.join(content) + '）至子频道' + str(channel))
        return post_return_dict

    def send_ark_24(self, desc: str, title: str, metadesc: str, link: str or None, msg_id: str or None = None,
                    channel: str or None = None, prompt: str or None = None, image: str = None,
                    subtitile: str = None) -> dict:
        """
        发送ark（id=24）模板消息的API，注意一般仅私域机器人可使用此API
        :param desc: 描述文本，string类型
        :param title: 标题文本，string类型
        :param metadesc: 详情描述文本，string类型
        :param link: 链接url，string类型
        :param msg_id: 消息id，从机器人接收到的消息中获取，如无则消息为主动消息
        :param channel: 子频道id
        :param prompt: 消息弹窗通知的文本内容
        :param image: 略缩图url，不可发送本地图片
        :param subtitile: 子标题文本，string类型
        :return: 返回解析后的json数据
        """
        post_json = {'ark': {'template_id': 24, 'kv': [{'key': '#DESC#', 'value': desc},
                                                       {'key': '#PROMPT#', 'value': prompt},
                                                       {'key': '#TITLE#', 'value': title},
                                                       {'key': '#METADESC#', 'value': metadesc},
                                                       {'key': '#IMG#', 'value': image},
                                                       {'key': '#LINK#', 'value': link},
                                                       {'key': '#SUBTITLE#', 'value': subtitile}]}, 'msg_id': msg_id}
        post_return = session.post(self.bot_url + '/channels/{}/messages'.format(channel),
                                   json=post_json, headers=self.header)
        post_return_dict = post_return.json()
        post_return_dict['header'] = post_return.headers
        self.logger.info('发送ark[id=24]消息（' + title + '//' + metadesc + '）至子频道' + str(channel))
        return post_return_dict

    def send_ark_37(self, title: str, content: str, link: str = None, msg_id: str or None = None,
                    channel: str or None = None, prompt: str or None = None, image: str = None) -> dict:
        """
        发送ark（id=37）模板消息的API，注意一般仅私域机器人可使用此API
        :param title: 标题文本，string类型
        :param content: 内容文本，string类型
        :param link: 链接url，string类型
        :param msg_id: 消息id，从机器人接收到的消息中获取，如无则消息为主动消息
        :param channel: 子频道id
        :param prompt: 消息弹窗通知的文本内容
        :param image: 略缩图url，不可发送本地图片
        :return: 返回解析后的json数据
        """
        post_json = {"ark": {"template_id": 37, "kv": [{"key": "#PROMPT#", "value": prompt},
                                                       {"key": "#METATITLE#", "value": title},
                                                       {"key": "#METASUBTITLE#", "value": content},
                                                       {"key": "#METACOVER#", "value": image},
                                                       {"key": "#METAURL#", "value": link}]}, 'msg_id': msg_id}
        post_return = session.post(self.bot_url + '/channels/{}/messages'.format(channel),
                                   json=post_json, headers=self.header)
        post_return_dict = post_return.json()
        post_return_dict['header'] = post_return.headers
        self.logger.info('发送ark[id=37]消息（' + title + '//' + content + '）至子频道' + str(channel))
        return post_return_dict

    def create_dm(self, target: str, guild: str) -> dict:
        """
        当机器人主动跟用户私信时，创建并获取一个虚拟频道id的API
        :param target: 目标用户id
        :param guild: 机器人跟目标用户所在的频道id
        :return: 返回解析后的json数据，注意发送私信仅需要使用guild_id这一项虚拟频道id的数据
        """
        post_json = {"recipient_id": target, "source_guild_id": guild}
        post_return = session.post(self.bot_url + '/users/@me/dms', json=post_json, headers=self.header)
        post_return_dict = post_return.json()
        post_return_dict['header'] = post_return.headers
        self.logger.info('创建私信虚拟频道（目标id：' + target + '）成功')
        return post_return_dict

    def send_dm(self, msg: str, msg_id: str = None, guild: str = None, image: str or None = None) -> dict:
        """
        私信用户的API
        :param msg: 消息主体
        :param msg_id: 消息id，从机器人接收到的消息中获取，如无则消息为主动消息
        :param guild: 虚拟频道id（非子频道id），从用户主动私信机器人的事件、或机器人主动创建私信的API中获取
        :param image: 图片url，不可发送本地图片，此url须在机器人平台后台先行报备
        :return: 返回解析后的json数据
        """
        post_json = {'content': msg, 'msg_id': msg_id, 'image': image}
        post_return = session.post(self.bot_url + f'/dms/{guild}/messages', json=post_json, headers=self.header)
        post_return_dict = post_return.json()
        post_return_dict['header'] = post_return.headers
        try:
            self.logger.info('发送（' + msg + '）至私信频道' + str(guild))
        except UnicodeEncodeError:
            self.logger.info('发送消息至私信频道' + str(guild))
            pass
        return post_return_dict

    def delete_msg(self, msg_id: str, channel: str, hidetip: bool = False) -> bool:
        """
        撤回消息的API，注意一般情况下仅私域可以使用
        :param msg_id: 目标消息的消息id，从机器人接收到的消息中获取
        :param channel: 子频道id
        :param hidetip: 是否隐藏提示小灰条，True为隐藏，False 为显示。默认为False
        :return: 返回成功或不成功的bool值
        """
        delete_return = session.delete(self.bot_url +
                                       f'/channels/{channel}/messages/{msg_id}?hidetip={str(hidetip).lower()}',
                                       headers=self.header)
        if delete_return.status_code == 200:
            return True
        return False

    def get_me_guilds(self) -> list:
        """
        获取机器人所在的所有频道列表
        :return: 返回包含所有数据的一个list，列表每个项均为dict数据
        """
        get_return = session.get(f'{self.bot_url}/users/@me/guilds', headers=self.header).json()
        if len(get_return) == 100:
            get_return_con = session.get(f'{self.bot_url}/users/@me/guilds?after=' + get_return[-1]['id'],
                                         headers=self.header).json()
            self.logger.debug(get_return_con)
            for items in get_return_con:
                get_return.append(items)
            while True:
                if len(get_return_con) == 100:
                    get_return_con = session.get(f'{self.bot_url}/users/@me/guilds?after=' + get_return_con[-1]['id'],
                                                 headers=self.header).json()
                    self.logger.debug(get_return_con)
                    for items in get_return_con:
                        get_return.append(items)
                else:
                    break
        return get_return

    def get_guild_info(self, guild: str) -> dict:
        """
        获取频道详情信息
        :param guild: 频道id
        :return: 返回解析后的json数据
        """
        get_return = session.get(f'{self.bot_url}/guilds/{guild}', headers=self.header)
        get_return_dict = get_return.json()
        get_return_dict['header'] = get_return.headers
        return get_return_dict

    def get_guild_channels(self, guild: str) -> dict:
        """
        获取频道的所有子频道列表数据
        :param guild: 频道id
        :return: 返回解析后的json数据
        """
        get_return = session.get(f'{self.bot_url}/guilds/{guild}/channels', headers=self.header)
        get_return_dict = get_return.json()
        get_return_dict['header'] = get_return.headers
        return get_return_dict

    def get_user_info(self, guild: str, user_id: str) -> dict:
        """
        获取频道中某一成员的信息数据
        :param guild: 频道id
        :param user_id: 目标用户id
        :return: 返回解析后的json数据
        """
        get_return = session.get(f'{self.bot_url}/guilds/{guild}/members/{user_id}', headers=self.header)
        get_return_dict = get_return.json()
        get_return_dict['header'] = get_return.headers
        return get_return_dict

    def get_permission(self, guild: str, channel: str, path: str, method: str, desc: str or None) -> bool:
        """
        发送频道API接口权限授权链接到频道
        :param guild: 频道id
        :param channel: 子频道id
        :param path: 需求权限的请求路径，如/guilds/{guild_id}
        :param method: 需求权限的请求方法，如GET
        :param desc: 机器人申请对应的 API 接口权限后可以使用功能的描述
        :return: 返回成功或不成功
        """
        post_json = {"channel_id": channel, "api_identify": {"path": path, "method": method.upper()}, "desc": desc}
        get_return = session.post('{}/guilds/{}/api_permission/demand'.format(self.bot_url, guild),
                                  headers=self.header, json=post_json)
        get_return_dict = get_return.json()
        get_return_dict['header'] = get_return.headers
        self.logger.debug(get_return_dict)
        if get_return.status_code == (200 or 204):
            self.logger.info('发送权限请求信息到频道：' + guild)
            return True
        else:
            return False

    def get_roles(self, guild: str) -> dict:
        """
        获取频道当前的所有身份组列表
        :param guild: 频道id
        :return: 返回解析后的json数据
        """
        get_return = session.get(f'{self.bot_url}/guilds/{guild}/roles', headers=self.header)
        get_return_dict = get_return.json()
        get_return_dict['header'] = get_return.headers
        return get_return_dict

    def add_roles(self, user_id: str, guild: str, role: str) -> dict:
        """
        为频道指定成员添加指定身份组
        :param user_id: 目标用户的id
        :param guild: 目标频道guild id
        :param role: 身份组编号，可从例如get_roles函数获取
        :return: 如成功，返回的dict中code的值为0
        """
        get_return = session.put(f'{self.bot_url}/guilds/{guild}/members/{user_id}/roles/{role}', headers=self.header)
        if get_return.status_code == 204:
            return {'code': '0', 'return_msg': '成功', 'header': get_return.headers}
        else:
            try:
                get_return_dict = get_return.json()
                get_return_dict['header'] = get_return.headers
                return get_return_dict
            except JSONDecodeError:
                return {'code': '-1', 'return_msg': '不成功，未知错误原因', 'header': get_return.headers}

    def del_roles(self, user_id: str, guild: str, role: str) -> dict:
        """
        删除频道指定成员的指定身份组
        :param user_id: 目标用户的id
        :param guild: 目标频道guild id
        :param role: 身份组编号，可从例如get_roles函数获取
        :return: 如成功，返回的dict中code的值为0
        """
        get_return = session.delete(f'{self.bot_url}/guilds/{guild}/members/{user_id}/roles/{role}',
                                    headers=self.header)
        if get_return.status_code == 204:
            return {'code': '0', 'return_msg': '成功', 'header': get_return.headers}
        else:
            try:
                get_return_dict = get_return.json()
                get_return_dict['header'] = get_return.headers
                return get_return_dict
            except JSONDecodeError:
                return {'code': '-1', 'return_msg': '不成功，未知错误原因', 'header': get_return.headers}

    def get_bot_id(self) -> str or None:
        """
        获取机器人在频道场景的用户ID
        :return: 返回机器人用户ID，如未注册则返回None
        """
        try:
            return self.bot_classes[0].bot_qid
        except IndexError:
            return None

    def start(self):
        """
        开始运行机器人的函数，在唤起此函数后的代码将不能运行，如需运行后续代码，请以多进程方式唤起此函数
        """
        self.running = True
        for i in range(self.shard_no, self.shard):
            self.bot_classes.append(BotWs(self.logger, self.shard, self.shard_no, self.url, self.header, self.bot_id,
                                          self.bot_token, self.bot_url, self.on_msg_function, self.on_dm_function,
                                          self.on_delete_function, self.is_filter_self, self.on_guild_event_function,
                                          self.on_guild_member_function, self.on_reaction_function,
                                          self.on_interaction_function, self.on_audit_function, self.on_forum_function,
                                          self.on_audio_function, self.intents, self.msg_treat, self.dm_treat))
            self.shard_no += 1
        for bot_class in self.bot_classes:
            self.bot_threads.append(Thread(target=bot_class.ws_starter))
        for bot_thread in self.bot_threads:
            bot_thread.setDaemon(True)
            bot_thread.start()
        if self.on_start_function is not None:
            self.on_start_function()
        time_thread = Thread(target=self.time_event_check)
        time_thread.setDaemon(True)
        time_thread.start()
        time_thread.join()

    def close(self):
        """
        结束运行机器人的函数
        """
        self.running = False
        self.bot_threads = []
        for bot_class in self.bot_classes:
            self.bot_threads.append(Thread(target=bot_class.ws_closer))
        for bot_thread in self.bot_threads:
            bot_thread.setDaemon(True)
            bot_thread.start()
        self.logger.info('所有WS链接已结束')


session = Session()
session.keep_alive = False
retry = Retry(total=4, connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
security_header = {'Content-Type': 'application/json', 'charset': 'UTF-8'}
