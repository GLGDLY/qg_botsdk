#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os
from logging import getLogger
from re import compile as re_compile

import pytest

import qg_botsdk

from ._base_context import _callback, bot, bot_async, config, plugin_path


def _repeat_or_start():
    pass


async def _async_repeat_or_start():
    pass


async def _queue_task(start_time: list):
    start_time.append(asyncio.get_event_loop().time())
    await asyncio.sleep(0.5)


@pytest.mark.run_order(1)
class TestBase:
    @staticmethod
    @pytest.mark.timeout(5)
    def test_base():
        bot = qg_botsdk.BOT(bot_id=config["bot_id"], bot_token=config["bot_token"])
        assert bot.bot_id == config["bot_id"]
        assert bot.bot_token == config["bot_token"]
        assert not bot.is_async
        assert not bot.is_private
        assert bot.bot_url == r"https://api.sgroup.qq.com"
        assert bot.no_permission_warning
        assert bot._http_session._is_retry
        assert bot._http_session._is_log_error
        assert bot._shard_no == 0
        assert bot._total_shard == 1
        assert bot.max_workers == 32
        assert bot._http_session._queue._MAX_RUNNING_SLOTS == 0
        assert bot._http_session._timeout.total == 20
        assert bot._intents == 0
        assert bot.bot_headers == {
            "Authorization": f'Bot {config["bot_id"]}.{config["bot_token"]}'
        }
        assert (
            str(bot)
            == f'<qg_botsdk.BOT object [id: {config["bot_id"]}, token: {config["bot_token"]}]>'
        )

        bot = qg_botsdk.BOT(
            bot_id=config["bot_id"], bot_token=config["bot_token"], is_async=True
        )
        assert bot.is_async
        bot = qg_botsdk.BOT(
            bot_id=config["bot_id"], bot_token=config["bot_token"], is_private=True
        )
        assert bot.is_private
        bot = qg_botsdk.BOT(
            bot_id=config["bot_id"], bot_token=config["bot_token"], is_sandbox=True
        )
        assert bot.bot_url == r"https://sandbox.api.sgroup.qq.com"
        bot = qg_botsdk.BOT(
            bot_id=config["bot_id"],
            bot_token=config["bot_token"],
            no_permission_warning=False,
        )
        assert not bot.no_permission_warning
        bot = qg_botsdk.BOT(
            bot_id=config["bot_id"], bot_token=config["bot_token"], is_retry=False
        )
        assert not bot._http_session._is_retry
        bot = qg_botsdk.BOT(
            bot_id=config["bot_id"], bot_token=config["bot_token"], is_log_error=False
        )
        assert not bot._http_session._is_log_error
        bot = qg_botsdk.BOT(
            bot_id=config["bot_id"],
            bot_token=config["bot_token"],
            shard_no=0,
            total_shard=2,
        )
        assert bot._shard_no == 0
        assert bot._total_shard == 2
        bot = qg_botsdk.BOT(
            bot_id=config["bot_id"],
            bot_token=config["bot_token"],
            shard_no=1,
            total_shard=2,
        )
        assert bot._shard_no == 1
        assert bot._total_shard == 2
        bot = qg_botsdk.BOT(
            bot_id=config["bot_id"], bot_token=config["bot_token"], max_workers=64
        )
        assert bot.max_workers == 64
        bot = qg_botsdk.BOT(
            bot_id=config["bot_id"],
            bot_token=config["bot_token"],
            api_max_concurrency=5,
        )
        assert bot._http_session._queue._MAX_RUNNING_SLOTS == 5
        bot = qg_botsdk.BOT(
            bot_id=config["bot_id"], bot_token=config["bot_token"], api_timeout=60
        )
        assert bot._http_session._timeout.total == 60

        with pytest.raises(DeprecationWarning):
            bot = qg_botsdk.BOT(
                bot_id=config["bot_id"], bot_token=config["bot_token"], bot_secret="xxx"
            )
        with pytest.raises(Exception) as e:
            bot = qg_botsdk.BOT(bot_id="", bot_token="")
            assert e.__name__ == "IdTokenMissing"
        with pytest.raises(Exception) as e:
            bot = qg_botsdk.BOT(bot_id="xxx", bot_token="xxx")
            bot.start()
            assert e.__name__ == "IdTokenError"

        assert "__sdk_default_logger" not in qg_botsdk.Plugins.get_preprocessor_names()
        bot.load_default_msg_logger()
        preprocessors = [x for x in qg_botsdk.Plugins.get_preprocessor_names()]
        assert "__sdk_default_logger" in preprocessors
        bot.load_default_msg_logger()
        assert preprocessors == [x for x in qg_botsdk.Plugins.get_preprocessor_names()]

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_msg(bot):
        bot.is_private = False
        bot.bind_msg(_callback)
        assert bot._intents == 1 << 30
        bot._intents = 0
        assert bot._func_registers.get("on_msg", None) == _callback
        assert bot.msg_treat

        bot.bind_msg(_callback, all_msg=True)
        assert bot._intents == 1 << 9
        bot._intents = 0

        bot.bind_msg(_callback, all_msg=False)
        assert bot._intents == 1 << 30
        bot._intents = 0

        bot.is_private = True
        bot.bind_msg(_callback, treated_data=False)
        assert bot._intents == 1 << 9
        assert not bot.msg_treat

        bot._func_registers = {}
        bot.bind_msg()(_callback)  # test decorator
        assert bot._func_registers.get("on_msg", None) == _callback

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_dm(bot):
        bot.bind_dm(_callback)
        assert bot._intents == 1 << 12
        assert bot.dm_treat
        assert bot._func_registers.get("on_dm", None) == _callback
        bot._intents = 0

        bot.bind_dm(_callback, treated_data=False)
        assert not bot.dm_treat

        bot._func_registers = {}
        bot.bind_dm()(_callback)  # test decorator
        assert bot._func_registers.get("on_dm", None) == _callback

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_msg_delete(bot):
        bot.is_private = False
        bot.bind_msg_delete(_callback)
        assert bot._intents == 1 << 30
        bot._intents = 0

        bot.is_private = True
        bot.bind_msg_delete(_callback)
        assert bot._intents == 1 << 9

        del_is_filter_self = bot._func_registers.get("del_is_filter_self", None)
        assert del_is_filter_self is not None and del_is_filter_self
        assert bot._func_registers.get("on_delete", None) == _callback

        bot.bind_msg_delete(_callback, is_filter_self=False)
        del_is_filter_self = bot._func_registers.get("del_is_filter_self", None)
        assert del_is_filter_self is not None and not del_is_filter_self

        bot._func_registers = {}
        bot.bind_msg_delete()(_callback)  # test decorator
        assert bot._func_registers.get("on_delete", None) == _callback

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_guild_event(bot):
        bot.bind_guild_event(_callback)
        assert bot._intents == 1
        assert bot._func_registers.get("on_guild_event", None) == _callback

        bot._func_registers = {}
        bot.bind_guild_event()(_callback)  # test decorator
        assert bot._func_registers.get("on_guild_event", None) == _callback

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_channel_event(bot):
        bot.bind_channel_event(_callback)
        assert bot._intents == 1
        assert bot._func_registers.get("on_channel_event", None) == _callback

        bot._func_registers = {}
        bot.bind_channel_event()(_callback)

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_guild_member(bot):
        bot.bind_guild_member(_callback)
        assert bot._intents == 1 << 1
        assert bot._func_registers.get("on_guild_member", None) == _callback

        bot._func_registers = {}
        bot.bind_guild_member()(_callback)

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_reaction(bot):
        bot.bind_reaction(_callback)
        assert bot._intents == 1 << 10
        assert bot._func_registers.get("on_reaction", None) == _callback

        bot._func_registers = {}
        bot.bind_reaction()(_callback)

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_interaction(bot):
        bot.bind_interaction(_callback)
        assert bot._intents == 1 << 26
        assert bot._func_registers.get("on_interaction", None) == _callback

        bot._func_registers = {}
        bot.bind_interaction()(_callback)

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_audit(bot):
        bot.bind_audit(_callback)
        assert bot._intents == 1 << 27
        assert bot._func_registers.get("on_audit", None) == _callback

        bot._func_registers = {}
        bot.bind_audit()(_callback)

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_forum(bot):
        bot.bind_forum(_callback)
        assert bot._intents == 1 << 28
        assert bot._func_registers.get("on_forum", None) == _callback

        bot._func_registers = {}
        bot.bind_forum()(_callback)

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_open_forum(bot):
        bot.bind_open_forum(_callback)
        assert bot._intents == 1 << 18
        assert bot._func_registers.get("on_open_forum", None) == _callback

        bot._func_registers = {}
        bot.bind_open_forum()(_callback)

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_audio(bot):
        bot.bind_audio(_callback)
        assert bot._intents == 1 << 29
        assert bot._func_registers.get("on_audio", None) == _callback

        bot._func_registers = {}
        bot.bind_audio()(_callback)

    @staticmethod
    @pytest.mark.timeout(5)
    def test_bind_live_channel_member(bot):
        bot.bind_live_channel_member(_callback)
        assert bot._intents == 1 << 19
        assert bot._func_registers.get("on_live_channel_member", None) == _callback

        bot._func_registers = {}
        bot.bind_live_channel_member()(_callback)

    @staticmethod
    @pytest.mark.timeout(5)
    def test_register_repeat_event(bot):
        bot.register_repeat_event(_repeat_or_start)
        assert bot._repeat_function == _repeat_or_start

        bot._repeat_function = None
        bot.register_repeat_event()(_repeat_or_start)
        assert bot._repeat_function == _repeat_or_start

    @staticmethod
    @pytest.mark.timeout(5)
    def test_register_start_event(bot):
        bot.register_start_event(_repeat_or_start)
        assert bot._on_start_function == _repeat_or_start

        bot._on_start_function = None
        bot.register_start_event()(_repeat_or_start)
        assert bot._on_start_function == _repeat_or_start

        with pytest.raises(TypeError):
            bot.register_start_event(_async_repeat_or_start)

    @staticmethod
    @pytest.mark.timeout(5)
    def test_async_register_start_event(bot_async):
        bot_async.register_start_event(_async_repeat_or_start)
        assert bot_async._on_start_function == _async_repeat_or_start

        bot_async._on_start_function = None
        bot_async.register_start_event()(_async_repeat_or_start)
        assert bot_async._on_start_function == _async_repeat_or_start

        with pytest.raises(TypeError):
            bot_async.register_start_event(_repeat_or_start)

    @staticmethod
    @pytest.mark.timeout(5)
    def test_security_setup(bot):
        bot.security_setup(config["mini_id"], config["mini_token"])

    @staticmethod
    def plugin_assert(bot):
        assert [x for x in qg_botsdk.Plugins.get_commands_names()] == ["plugins_test"]
        assert [x for x in qg_botsdk.Plugins.get_preprocessor_names()] == [
            "before_command_test"
        ]
        plugins_list = bot._retrieve_new_plugins()
        assert len(plugins_list) == 2
        command_list = plugins_list[0]
        before_command_list = plugins_list[1]
        assert len(command_list) == 1
        assert len(before_command_list) == 1
        assert command_list[0].command == ["plugins_test"]

    @pytest.mark.timeout(5)
    def test_load_plugins(self, bot):
        bot._retrieve_new_plugins()  # clear plugins before first

        from . import _testing_plugin

        self.plugin_assert(bot)

        assert bot._retrieve_new_plugins() == ([], [])

        bot.load_plugins(plugin_path)
        self.plugin_assert(bot)

        with pytest.raises(ModuleNotFoundError):
            bot.load_plugins("xxx")

    @staticmethod
    def direct_plugin_assert(bot, regex=False):
        assert [x for x in qg_botsdk.Plugins.get_commands_names()] == ["_callback"]
        assert [x for x in qg_botsdk.Plugins.get_preprocessor_names()] == ["<lambda>"]
        plugins_list = bot._retrieve_new_plugins()
        assert len(plugins_list) == 2
        command_list = plugins_list[0]
        before_command_list = plugins_list[1]
        assert len(command_list) == 1
        assert len(before_command_list) == 1
        if regex:
            assert command_list[0].regex == [re_compile(r"command_(\s)")]
        else:
            assert command_list[0].command == ["abc"]

    @pytest.mark.timeout(5)
    def test_direct_load_plugins(self, bot):
        bot._retrieve_new_plugins()  # clear plugins before first

        bot.on_command("abc")(_callback)
        bot.before_command()(lambda x: x)
        self.direct_plugin_assert(bot)

        assert bot._retrieve_new_plugins() == ([], [])

        bot.on_command(["abc"])(_callback)
        bot.before_command()(lambda x: x)
        self.direct_plugin_assert(bot)

        assert bot._retrieve_new_plugins() == ([], [])

        bot.on_command(regex=r"command_(\s)")(_callback)
        bot.before_command()(lambda x: x)
        self.direct_plugin_assert(bot, regex=True)

        assert bot._retrieve_new_plugins() == ([], [])

        bot.on_command(regex=re_compile(r"command_(\s)"))(_callback)
        bot.before_command()(lambda x: x)
        self.direct_plugin_assert(bot, regex=True)

    @staticmethod
    @pytest.mark.timeout(5)
    def test_logger(caplog):
        _log_path = "./log/test_log_file"
        if os.path.exists(_log_path):
            for _file in os.listdir(_log_path):
                os.remove(os.path.join(_log_path, _file))
            os.rmdir(_log_path)
        logger = qg_botsdk.Logger("test_logger", _log_path)
        logger.info("test")
        assert os.path.exists(_log_path)
        assert len(os.listdir(_log_path)) == 1

        logger = qg_botsdk.Logger("test_logger", _log_path)
        logger.set_formatter(info_format="[%(levelname)s] %(message)s")
        logger.info("test")
        assert os.path.exists(_log_path)
        assert len(os.listdir(_log_path)) == 1

        logger.disable_logger("a")
        assert getLogger("a").disabled
        logger.disable_logger(["b", "c"])
        assert getLogger("b").disabled
        assert getLogger("c").disabled

    @staticmethod
    @pytest.mark.timeout(5)
    def test_queue():
        queue = qg_botsdk._queue.Queue(1)
        loop = asyncio.get_event_loop()
        start_time_arr = []
        loop.create_task(queue.create_task(_queue_task, start_time_arr))
        loop.run_until_complete(asyncio.sleep(0.1))
        loop.run_until_complete(queue.create_task(_queue_task, start_time_arr))
        assert start_time_arr[1] - start_time_arr[0] >= 0.5

    @staticmethod
    @pytest.mark.timeout(5)
    def test_func_checking(bot):
        with pytest.raises(TypeError):
            bot.bind_msg()(lambda x, y, z: print(x, y, z))

    @staticmethod
    @pytest.mark.timeout(5)
    def test_convert_color_util():
        assert qg_botsdk.utils.convert_color((255, 254, 253)) == 16645887
        assert qg_botsdk.utils.convert_color("#fffefd") == 16645887
        assert qg_botsdk.utils.convert_color("#FFFEFD") == 16645887
        with pytest.raises(TypeError):
            qg_botsdk.utils.convert_color("fffefg")
        with pytest.raises(TypeError):
            qg_botsdk.utils.convert_color("fffefdd")
        with pytest.raises(TypeError):
            qg_botsdk.utils.convert_color((255, 254, 253, 252))
        with pytest.raises(TypeError):
            qg_botsdk.utils.convert_color((255, 254, 256))
        with pytest.raises(TypeError):
            qg_botsdk.utils.convert_color(255)
