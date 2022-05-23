# !/usr/bin/env python3
# encoding: utf-8
from sys import exc_info
from traceback import extract_tb
from inspect import stack
from json import loads, dumps
from json.decoder import JSONDecodeError
import aiohttp
from ssl import SSLContext
from typing import Any, Callable
from asyncio import new_event_loop, all_tasks, set_event_loop, sleep
from time import sleep as t_sleep
from threading import Thread
from .utils import objectize


def __getattr__(identifier: str) -> object:
    if stack()[1].filename.split('\\')[-1] != 'qg_bot.py':
        raise AssertionError("此为SDK内部使用文件，无法使用，注册机器人请使用from qg_bot.py import BOT")

    return globals()[identifier.__path__]


class BotWs:
    def __init__(self, session, logger, shard: int, shard_no: int, url: str, bot_id: str, bot_token: str,
                 bot_url: str, on_msg_function: Callable[[Any], Any], on_dm_function: Callable[[Any], Any],
                 on_delete_function: Callable[[Any], Any], is_filter_self: bool,
                 on_guild_event_function: Callable[[Any], Any], on_guild_member_function: Callable[[Any], Any],
                 on_reaction_function: Callable[[Any], Any], on_interaction_function: Callable[[Any], Any],
                 on_audit_function: Callable[[Any], Any], on_forum_function: Callable[[Any], Any],
                 on_audio_function: Callable[[Any], Any], intents: int, msg_treat: bool, dm_treat: bool,
                 on_start_function: Callable[[], Any]):
        if stack()[1].filename.split('\\')[-1] != 'qg_bot.py':
            raise AssertionError("此为SDK内部使用类，无法使用，注册机器人请使用from qg_bot.py import BOT")
        self.session = session
        self.logger = logger
        self.shard = shard
        self.shard_no = shard_no
        self.url = url
        self.bot_id = bot_id
        self.bot_token = bot_token
        self.bot_url = bot_url
        self.on_start_function = on_start_function
        self.flag = False
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
        self.loop = new_event_loop()
        self.heart_paras = {"op": 1, "d": 'null'}
        self.reconnect_times = 0
        self.connection = True
        self.re_connect = False
        self.running = False
        self.session_id = 0
        self.heartbeat = None

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
        if not self.ws.closed:
            await self.ws.send_str(msg)

    async def heart(self):
        while True:
            await sleep(self.heartbeat_time)
            if not self.ws.closed:
                await self.ws.send_str(dumps(self.heart_paras))

    def data_process(self, data):
        data["d"]["t"] = data["t"]
        data["d"]["event_id"] = data["id"]
        try:
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
                    if self.msg_treat and raw_msg:
                        if '\xa0' in raw_msg:
                            raw_msg = raw_msg.replace('\xa0', ' ')
                        if raw_msg[0] == '/':
                            raw_msg = raw_msg[1:]
                        data["d"]["treated_msg"] = raw_msg.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;',
                                                                                                              '>')
                    Thread(target=self.on_msg_function, args=[objectize(data["d"])],
                           name=f'MsgThread-{str(data["s"])}').start()
            elif data["t"] in ("MESSAGE_DELETE", "PUBLIC_MESSAGE_DELETE", "DIRECT_MESSAGE_DELETE"):
                if self.on_delete_function is not None:
                    if self.is_filter_self:
                        target = data['d']['message']['author']['id']
                        op_user = data['d']['op_user']['id']
                        if op_user == target:
                            return
                    Thread(target=self.on_delete_function, args=[objectize(data["d"])],
                           name=f'MsgThread-{str(data["s"])}').start()
            elif data["t"] == "DIRECT_MESSAGE_CREATE":
                if 'content' not in data["d"]:
                    raw_msg = ''
                else:
                    raw_msg = data["d"]["content"]
                self.logger.info('收到来自“' + data["d"]["author"]["username"] + '--' + str(data["d"]["author"]["id"])
                                 + '”的私信消息（' + raw_msg + '）')
                if self.on_dm_function is not None:
                    if self.msg_treat and raw_msg:
                        if '\xa0' in raw_msg:
                            raw_msg = raw_msg.replace('\xa0', ' ')
                        if raw_msg[0] == '/':
                            raw_msg = raw_msg[1:]
                        raw_msg = raw_msg.strip()
                        raw_msg = raw_msg.replace('&amp;', '&')
                        raw_msg = raw_msg.replace('&lt;', '<')
                        raw_msg = raw_msg.replace('&gt;', '>')
                        data["d"]["treated_msg"] = raw_msg
                    Thread(target=self.on_dm_function, args=[objectize(data["d"])],
                           name=f'MsgThread-{str(data["s"])}').start()
            elif data["t"] in ("GUILD_CREATE", "GUILD_UPDATE", "GUILD_DELETE", "CHANNEL_CREATE", "CHANNEL_UPDATE",
                               "CHANNEL_DELETE"):
                if self.on_guild_event_function is not None:
                    Thread(target=self.on_guild_event_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
            elif data["t"] in ("GUILD_MEMBER_ADD", "GUILD_MEMBER_UPDATE", "GUILD_MEMBER_REMOVE"):
                if self.on_guild_member_function is not None:
                    Thread(target=self.on_guild_member_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
            elif data["t"] in ("MESSAGE_REACTION_ADD", "MESSAGE_REACTION_REMOVE"):
                print(data)
                if self.on_reaction_function is not None:
                    Thread(target=self.on_reaction_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
            elif data["t"] == "INTERACTION_CREATE":
                if self.on_interaction_function is not None:
                    Thread(target=self.on_interaction_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
            elif data["t"] in ("MESSAGE_AUDIT_PASS", "MESSAGE_AUDIT_REJECT"):
                if self.on_audit_function is not None:
                    Thread(target=self.on_audit_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
            elif data["t"] in ("FORUM_THREAD_CREATE", "FORUM_THREAD_UPDATE", "FORUM_THREAD_DELETE", "FORUM_POST_CREATE",
                               "FORUM_POST_DELETE", "FORUM_REPLY_CREATE", "FORUM_REPLY_DELETE",
                               "FORUM_PUBLISH_AUDIT_RESULT"):
                if self.on_forum_function is not None:
                    for items in ["content", "title"]:
                        try:
                            data["d"]["thread_info"][items] = loads(data["d"]["thread_info"][items])
                        except JSONDecodeError:
                            pass
                    Thread(target=self.on_forum_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
            elif data["t"] in ("AUDIO_START", "AUDIO_FINISH", "AUDIO_ON_MIC", "AUDIO_OFF_MIC"):
                if self.on_audio_function is not None:
                    Thread(target=self.on_audio_function, args=[objectize(data["d"])],
                           name=f'EventThread-{str(data["s"])}').start()
        except Exception as error:
            self.logger.error(error)
            error_info = extract_tb(exc_info()[-1])[-1]
            self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0],
                                                                              error_info[1], error_info[2]))
            return

    def main(self, msg):
        data = loads(msg)
        if data["op"] == 11:
            self.logger.debug('心跳发送成功')
        elif data["op"] == 9:
            self.logger.error('[错误] 参数出错（一般此报错为传递了无权限的事件订阅，请检查是否有权限订阅相关事件）')
            exit()
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
                me_qid = self.session.get(self.bot_url + '/users/@me').json()
                self.bot_qid = str(me_qid['id'])
                self.logger.info('机器人频道用户ID：' + self.bot_qid)
                self.connection = True
                self.session_id = data["d"]["session_id"]
                self.reconnect_times = 0
                tasks = [task.get_name() for task in all_tasks()]
                if 'heartbeat_task' not in tasks:
                    self.heartbeat = self.loop.create_task(self.heart())
                    self.heartbeat.set_name('heartbeat_task')
                self.logger.info('连接成功，机器人开始运行')
                if self.on_start_function is not None and not self.flag:
                    self.flag = True
                    self.on_start_function()
            elif data["t"] == "RESUMED":
                self.connection = True
                self.reconnect_times = 0
                tasks = [task.get_name() for task in all_tasks()]
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
            async with aiohttp.ClientSession() as ws_session:
                async with ws_session.ws_connect(self.url, ssl=SSLContext()) as self.ws:
                    while self.running:
                        message = await self.ws.receive()
                        if message.type == aiohttp.WSMsgType.TEXT:
                            if not self.running:
                                if self.heartbeat is not None and not self.heartbeat.cancelled():
                                    self.heartbeat.cancel()
                                await self.ws.close()
                                self.logger.info('WS进程已结束')
                                return
                            self.main(message.data)
                        elif message.type == aiohttp.WSMsgType.CLOSE:
                            if self.running:
                                self.connection = False
                                self.re_connect = True
                                if self.heartbeat is not None and not self.heartbeat.cancelled():
                                    self.heartbeat.cancel()
                                self.logger.warning('BOT_WS链接已断开，正在尝试重连……')
                                return
        except Exception as error:
            self.logger.warning('BOT_WS链接已断开，正在尝试重连……')
            if self.heartbeat is not None and not self.heartbeat.cancelled():
                self.heartbeat.cancel()
            self.logger.error(error)
            error_info = extract_tb(exc_info()[-1])[-1]
            self.logger.debug("[error:{}] File \"{}\", line {}, in {}".format(error, error_info[0],
                                                                              error_info[1], error_info[2]))
            return

    def ws_starter(self):
        self.running = True
        self.re_connect = False
        set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())
        while self.running:
            if self.reconnect_times >= 20:
                self.re_connect = False
            try:
                self.loop.run_until_complete(self.connect())
                t_sleep(5)
            except aiohttp.WSServerHandshakeError:
                self.logger.warning('网络连线不稳定或已断开，请检查网络链接')
                t_sleep(5)
                pass
